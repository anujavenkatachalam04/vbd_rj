import streamlit as st
import pandas as pd
import json
import os
import tempfile
from datetime import timedelta
from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive
from oauth2client.service_account import ServiceAccountCredentials
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import re
from utils import load_drive, get_sorted_districts, get_sorted_subdistricts  # Use utils

st.set_page_config(page_title="Weekly Time Series - Dengue & Climate (May-Dec 2024)", layout="wide")

# --- Load data from Google Drive only if not downloaded ---
csv_path = "time_series_dashboard.csv"
file_id = "1ad-PcGSpk6YoO-ZolodMWfvFq64kO-Z_"  # Set your correct file ID here

if not os.path.exists(csv_path):
    drive = load_drive(st.secrets["gdrive_creds"])
    downloaded = drive.CreateFile({'id': file_id})
    downloaded.GetContentFile(csv_path)

# --- Load CSV ---
@st.cache_data
def load_weekly_data():
    df = pd.read_csv(csv_path, parse_dates=["week_start_date"])
    df['dtname'] = df['dtname'].astype(str).str.strip()
    df['sdtname'] = df['sdtname'].astype(str).str.strip()
    df['dtname_disp'] = df['dtname_disp'].astype(str).str.strip()
    df['sdtname_disp'] = df['sdtname_disp'].astype(str).str.strip()
    return df

df = load_weekly_data()

# --- Sidebar filters ---
districts = get_sorted_districts(df)
selected_dt = st.sidebar.selectbox("Select District", districts)
subdistricts = get_sorted_subdistricts(df[df['dtname_disp'] == selected_dt])
selected_sdt = st.sidebar.selectbox("Select Block", subdistricts)

# --- Filter based on selection ---
filtered = df[(df['dtname_disp'] == selected_dt) & (df['sdtname_disp'] == selected_sdt)]
if filtered.empty:
    st.warning("No data available for this selection.")
    st.stop()

filtered = filtered.sort_values("week_start_date")
week_dates = filtered["week_start_date"]
x_start = filtered["week_start_date"].min()
x_end = filtered["week_start_date"].max()

# --- Extract lags ---
trigger = filtered["trigger_date"].iloc[0]
lag_all = filtered["lag_all_weeks"].iloc[0]
lag_min = filtered["lag_min_weeks"].iloc[0]
lag_max = filtered["lag_max_weeks"].iloc[0]
lag_hum = filtered["lag_hum_weeks"].iloc[0]
lag_rainfall = filtered["lag_rainfall_weeks"].iloc[0]

def fmt_lag(val):
    return f"{int(val)} week{'s' if int(val) != 1 else ''}" if pd.notna(val) else "Threshold not met continuously before trigger week"

subplot_titles = [
    f"Dengue Cases (Mean Maximum Temperature ≤ 35°C AND Mean Minimum Temperature ≥ 18°C OR Relative Humidity between 60% and 80%: {fmt_lag(lag_all)}",
    f"Mean Maximum Temperature (°C) (Threshold:≤ 35°C; Lag: {fmt_lag(lag_max)})",
    f"Mean Minimum Temperature (°C) (Threshold:≥ 18°C; Lag: {fmt_lag(lag_min)})",
    f"Mean Relative Humidity (%) (Threshold:between(60, 80); Lag: {fmt_lag(lag_hum)})",
    f"Total Rainfall (mm) (Threshold:between(0.5, 150); Lag: {fmt_lag(lag_rainfall)})"
]

fig = make_subplots(
    rows=5, cols=1, shared_xaxes=False,
    vertical_spacing=0.05,
    subplot_titles=subplot_titles
)

# --- Add Traces ---
def add_trace(row, col, y_data_col, trace_name, color, highlight_cond=None, highlight_color=None, lag_val=None):
    fig.add_trace(go.Scatter(
        x=week_dates,
        y=filtered[y_data_col],
        name=trace_name,
        mode="lines+markers",
        marker=dict(size=4),
        line=dict(color=color)
    ), row=row, col=col)

    fig.update_yaxes(
        title_text=trace_name,
        row=row,
        col=col,
        showgrid=True,
        zeroline=True,
        gridcolor='lightgray',
        tickfont=dict(size=12, color='black'),
        title_font=dict(size=12, color="black"),
        range=[0, None]
    )

    if highlight_cond is not None and highlight_color:
        highlight_weeks = filtered[highlight_cond]
        for dt in highlight_weeks["week_start_date"].drop_duplicates():
            fig.add_vrect(
                x0=dt,
                x1=dt + timedelta(days=6),
                fillcolor=highlight_color,
                opacity=0.1,
                line_width=0,
                layer="below",
                row=row, col=col
            )

    # --- Add vertical trigger line ---
    fig.add_vline(
        x=trigger,
        line=dict(color="black", width=2, dash="dash"),
        row=row, col=col
    )

    # --- Add vertical threshold line ---
    if lag_val is not None and pd.notna(lag_val):
        try:
            threshold_date = trigger - timedelta(weeks=int(lag_val))
            fig.add_vline(
                x=threshold_date,
                line=dict(color="blue", width=2, dash="dot"),
                row=row, col=col
            )
        except (ValueError, TypeError) as e:
            print(f"[WARN] Skipping threshold line for '{trace_name}' due to invalid lag_val={lag_val}: {e}")


add_trace(1, 1, "dengue_cases", "Dengue Cases (Weekly Sum)", "crimson", highlight_cond=(filtered["meets_threshold"]), highlight_color="red", lag_val=lag_all)
add_trace(2, 1, "temperature_2m_max", "Max Temperature (°C) (Weekly Mean)", "orange", highlight_cond=(filtered["temperature_2m_max"] <= 35), highlight_color="orange", lag_val=lag_max)
add_trace(3, 1, "temperature_2m_min", "Min Temperature (°C) (Weekly Mean)", "blue", highlight_cond=(filtered["temperature_2m_min"] >= 18), highlight_color="blue", lag_val=lag_min)
add_trace(4, 1, "relative_humidity_2m_mean", "Mean Relative Humidity (%) (Weekly Mean)", "green", highlight_cond=(filtered["relative_humidity_2m_mean"].between(60, 80)), highlight_color="green", lag_val=lag_hum)
add_trace(5, 1, "rain_sum", "Rainfall (mm) (Weekly Sum)", "purple", highlight_cond=filtered["rain_sum"].between(0.5, 150, inclusive="both"), highlight_color="purple", lag_val=lag_rainfall)

for i in range(1, 6):
    fig.update_xaxes(
        row=i, col=1,
        tickangle=-45,
        tickformat="%d-%b-%y",
        tickfont=dict(size=10, color='black'),
        ticks="outside",
        showgrid=True,
        gridcolor='lightgray',
        dtick=604800000,
        range=[x_start, x_end],
        tick0=filtered["week_start_date"].iloc[0]
    )

fig.update_layout(
    height=2100,
    width=3000,
    title_text=f"Weekly Dengue and Climate Trends (May-December 2024) — Block: {selected_sdt}, District: {selected_dt}",
    showlegend=False,
    margin=dict(t=80, b=100),
    template=None,
    plot_bgcolor="white",
    paper_bgcolor="white",
    font=dict(color='black')
)

st.plotly_chart(fig, use_container_width=True)

pct_blocks = filtered["pct_blocks_with_cases"].iloc[0] if "pct_blocks_with_cases" in filtered.columns else None
if pd.notna(pct_blocks):
    st.markdown(f"<div style='font-size: 14px; color: gray; margin-top: -20px;'>"
                f"**{pct_blocks:.1f}%** of blocks in this district reported at least one dengue case between May 2024 and December 2024."
                f"</div>", unsafe_allow_html=True)

st.markdown("""
**Trigger Date: Week where a sustained sharp rise in dengue cases begins**
| Step | Description |
|------|-------------|
| 1    | Identify the week with **maximum dengue cases**. |
| 2    | Iterate **backwards** from that week to find the last week where dengue cases show a **strict decrease** each week. |
| 3    | From that point onward (i.e., when cases start to rise again), look for a sequence of **4 consecutive weeks** where each week has at least a **10-case increase** from the previous week. |
| 4    | The **first week** of this 4-week rising period is marked as the **trigger date**. |
| 5    | If this is not found for a block, the trigger date is the minimum date when cases start to strictly increase.|

** Districts with High Dengue Cases:
| S.No | District     | Dengue Cases |
|------|--------------|--------------|
| 1    | Jaipur       | 1601.0       |
| 2    | Udaipur      | 1170.0       |
| 3    | Bikaner      | 816.0        |
| 4    | Dausa        | 514.0        |
| 5    | Ganganagar   | 446.0        |

** Subdistricts with High Dengue Cases:
| Rank | District    | Subdistrict | Dengue Cases | 
|------|-------------|-------------|---------------|
| 1    | Jaipur      | Jaipur      | 780.0         | 
| 2    | Udaipur     | Girwa       | 748.0         | 
| 3    | Bikaner     | Bikaner     | 546.0         |
| 4    | Jaipur      | Sanganer    | 424.0         | 
| 5    | Ganganagar  | Ganganagar  | 352.0         | 
| 6    | Kota        | Ladpura     | 325.0         | 
""")

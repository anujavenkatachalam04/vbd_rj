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

st.set_page_config(page_title="Dengue Climate Dashboard", layout="wide")

# --- Load Google Drive credentials and file ---
@st.cache_resource
def load_drive():
    creds_json = st.secrets["gdrive_creds"]
    creds_dict = json.loads(creds_json)
    with tempfile.NamedTemporaryFile(mode='w+', delete=False) as tmp:
        json.dump(creds_dict, tmp)
        tmp.flush()
        gauth = GoogleAuth()
        gauth.credentials = ServiceAccountCredentials.from_json_keyfile_name(
            tmp.name,
            scopes=["https://www.googleapis.com/auth/drive"]
        )
        drive = GoogleDrive(gauth)
    return drive

# --- Download file if not exists ---
csv_path = "time_series_dashboard.csv"
if not os.path.exists(csv_path):
    drive = load_drive()
    file_id = "1ad-PcGSpk6YoO-ZolodMWfvFq64kO-Z_"  # Replace with your actual file ID
    downloaded = drive.CreateFile({'id': file_id})
    downloaded.GetContentFile(csv_path)

# --- Load CSV ---
@st.cache_data
def load_data():
    df = pd.read_csv(csv_path, parse_dates=["week_start_date"])
    df['dtname'] = df['dtname'].astype(str).str.strip()
    df['sdtname'] = df['sdtname'].astype(str).str.strip()
    df['high_incidence_district'] = df['high_incidence_district'].astype(bool)

    # Create dtname_disp
    df["dtname_disp"] = df.apply(
        lambda row: f"{row['dtname']} (High)" if row["high_incidence_district"] else row["dtname"],
        axis=1
    )

    if "meets_threshold" in df.columns:
        df["meets_threshold"] = df["meets_threshold"].astype(str).str.lower() == "true"
    return df

df = load_data()

# --- Sidebar filters ---
priority_districts = ['Jaipur (High)', 'Udaipur (High)', 'Bikaner (High)', 'Dausa (High)', 'Ajmer (High)']

# All districts from data
all_districts = sorted(set(df['dtname_disp'].unique()) - set(priority_districts) - {'All'})

# Combine with "All" at the top
districts = ["All"] + priority_districts + all_districts

selected_dt = st.sidebar.selectbox("Select District", districts)

subdistricts = ["All"] + sorted([s for s in df[df['dtname_disp'] == selected_dt]['sdtname'].unique() if s != "All"])
selected_sdt = st.sidebar.selectbox("Select Block", subdistricts)

# --- Filter based on selection ---
filtered = df[(df['dtname_disp'] == selected_dt) & (df['sdtname'] == selected_sdt)]
if filtered.empty:
    st.warning("No data available for this selection.")
    st.stop()

filtered = filtered.sort_values("week_start_date")
week_dates = filtered["week_start_date"]
x_start = filtered["week_start_date"].min()
x_end = filtered["week_start_date"].max()

# --- Extract lags ---
trigger = filtered["trigger_date"].iloc[0]
lag_all = filtered["lag_all"].iloc[0]
lag_min = filtered["lag_min"].iloc[0]
lag_max = filtered["lag_max"].iloc[0]
lag_hum = filtered["lag_hum"].iloc[0]

def fmt_lag(val):
    return f"{int(val)} day{'s' if int(val) != 1 else ''}" if pd.notna(val) else "–"

# --- Create Subplots with lag info in titles ---
subplot_titles = [
    f"Dengue Cases (Lag: {fmt_lag(lag_all)})",
    f"Max Temperature (°C) (Lag: {fmt_lag(lag_max)})",
    f"Min Temperature (°C) (Lag: {fmt_lag(lag_min)})",
    f"Mean Relative Humidity (%) (Lag: {fmt_lag(lag_hum)})",
    "Rainfall (mm)"
]

fig = make_subplots(
    rows=5, cols=1, shared_xaxes=False,
    vertical_spacing=0.05,
    subplot_titles=subplot_titles
)

# --- Add Traces ---
def add_trace(row, col, y_data_col, trace_name, color, highlight_cond=None, highlight_color=None):
    fig.add_trace(go.Scatter(
        x=week_dates,
        y=filtered[y_data_col],
        name=trace_name,
        mode="lines+markers",
        marker=dict(size=4),
        line=dict(color=color)
    ), row=row, col=col)

    # Set y-axis config
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

# Add all 5 plots
add_trace(1, 1, "dengue_cases", "Dengue Cases (Weekly Sum)", "crimson", highlight_cond=(filtered["meets_threshold"]), highlight_color="red")
add_trace(2, 1, "temperature_2m_max", "Max Temperature (°C) (Weekly Max)", "orange", highlight_cond=(filtered["temperature_2m_max"] <= 35), highlight_color="orange")
add_trace(3, 1, "temperature_2m_min", "Min Temperature (°C) (Weekly Min)", "blue", highlight_cond=(filtered["temperature_2m_min"] >= 18), highlight_color="blue")
add_trace(4, 1, "relative_humidity_2m_mean", "Mean Relative Humidity (%) (Weekly Mean)", "green", highlight_cond=(filtered["relative_humidity_2m_mean"] >= 60), highlight_color="green")
add_trace(5, 1, "rain_sum", "Rainfall (mm) (Weekly Sum)", "purple")

# --- X-axis config for all subplots ---
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
        range=[x_start, x_end]
    )

# --- Layout ---
fig.update_layout(
    height=2100,
    width=3000,
    title_text=f"Weekly Dengue and Climate Trends — Block: {selected_sdt}, District: {selected_dt}",
    showlegend=False,
    margin=dict(t=80, b=100),
    template=None,
    plot_bgcolor="white",
    paper_bgcolor="white",
    font=dict(color='black')
)

# --- Display Chart ---
st.plotly_chart(fig, use_container_width=True)

# --- Display % of blocks with at least one case ---
pct_blocks = filtered["pct_blocks_with_cases"].iloc[0] if "pct_blocks_with_cases" in filtered.columns else None
if pd.notna(pct_blocks):
    st.markdown(f"<div style='font-size: 14px; color: gray; margin-top: -20px;'>"
                f"**{pct_blocks:.1f}%** of blocks in this district reported at least one dengue case between June 2024 and June 2025."
                f"</div>", unsafe_allow_html=True)

# --- Threshold Notes ---
st.markdown("""
**Note on Thresholds**:
- **Dengue Cases**: Weeks shaded **red** indicate that Max Temperature (°C) ≤ 35°C AND Min Temperature (°C) ≥ 18°C OR Mean Relative Humidity (%) ≥ 60%.
- **Max Temperature (°C)**: Weeks shaded **orange** indicate values ≤ 35°C.
- **Min Temperature (°C)**: Weeks shaded **blue** indicate values ≥ 18°C.
- **Mean Relative Humidity (%)**: Weeks shaded **green** indicate values ≥ 60%.

**Note on Case Increase Detection**:
- An increase in cases is detected when **this week’s cases > last week’s**, and **last week’s > two weeks ago** — indicating a **two-week sustained rise** in dengue cases.
""")


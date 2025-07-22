import streamlit as st
import pandas as pd
import os
from datetime import timedelta
from plotly.subplots import make_subplots
import plotly.graph_objects as go
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
    f"Dengue Cases (Mean Max Temp ≤ 35°C AND Min Temp ≥ 18°C OR RH 60-80%): {fmt_lag(lag_all)}",
    f"Mean Maximum Temperature (°C) (Threshold: ≤ 35°C; Lag: {fmt_lag(lag_max)})",
    f"Mean Minimum Temperature (°C) (Threshold: ≥ 18°C; Lag: {fmt_lag(lag_min)})",
    f"Mean Relative Humidity (%) (Threshold: 60–80%; Lag: {fmt_lag(lag_hum)})",
    f"Total Rainfall (mm) (Threshold: 0.5–150 mm; Lag: {fmt_lag(lag_rainfall)})"
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

    if highlight

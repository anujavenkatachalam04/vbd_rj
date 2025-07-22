import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from utils import load_drive, get_sorted_districts
import json
import os
import tempfile
from datetime import timedelta
from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive
from oauth2client.service_account import ServiceAccountCredentials
import re

st.set_page_config(page_title="Monthly Dengue Trends (2022-2024)", layout="wide")

# --- Load Google Drive credentials and file ---
@st.cache_resource
def load_monthly_drive():
    creds_dict = dict(st.secrets["gdrive_creds"])
    return load_drive(creds_dict)

# --- Download file if not exists ---
csv_path = "dist_ts_dashboard.csv"
file_id="16UGTNwPCGs7fO5XN4vYahfa7mCnnMBxD"

if not os.path.exists(csv_path):
    drive = load_drive(st.secrets["gdrive_creds"])
    downloaded = drive.CreateFile({'id': file_id})
    downloaded.GetContentFile(csv_path)

# --- Load CSV ---
@st.cache_data
def load_monthly_data():
    df = pd.read_csv(csv_path)
    df['Year_Month'] = pd.to_datetime(df['Year_Month'], format="%Y-%m")
    df['dtname'] = df['dtname'].astype(str).str.strip()
    df['dtname_disp'] = df['dtname_disp'].astype(str).str.strip()
    return df

df = load_monthly_data()

# --- Sidebar filters ---
districts = get_sorted_districts(df)
selected_dt = st.sidebar.selectbox("Select District", districts)

# --- Filter based on selection ---
filtered = df[df['dtname_disp'] == selected_dt]
if filtered.empty:
    st.warning("No data available for this selection.")
    st.stop()

filtered = filtered.sort_values("Year_Month")
x_vals = filtered["Year_Month"]
x_start = filtered["Year_Month"].min()
x_end = filtered["Year_Month"].max()

fig = make_subplots(
    rows=5, cols=1, shared_xaxes=False,
    vertical_spacing=0.05,
  subplot_titles = [
    "Total Dengue Cases",
    "Mean Maximum Temperature",
    "Mean Minimum Temperature",
    "Mean Relative Humidity (%)",
    "Total Rainfall (mm)"
]
)

# --- Add Traces ---
def add_trace(row, col, y_data_col, trace_name, color):
    fig.add_trace(go.Scatter(
        x=x_vals,
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

add_trace(1, 1, "dengue_cases", "Dengue Cases (Monthly Sum)", "red")
add_trace(2, 1, "temperature_2m_max", "Max Temperature (°C) (Monthly Mean)", "orange")
add_trace(3, 1, "temperature_2m_min", "Min Temperature (°C) (Monthly Mean)", "blue")
add_trace(4, 1, "relative_humidity_2m_mean", "Mean Relative Humidity (%) (Monthly Mean)", "green")
add_trace(5, 1, "rain_sum", "Rainfall (mm) (Monthly Sum)", "purple")

for i in range(1, 6):
    fig.update_xaxes(
        row=i, col=1,
        tickangle=-45,
        tickformat="%b\n%Y",
        tickmode="linear",
        dtick="M1",  # Show  month
        tickfont=dict(size=10, color='black'),
        ticks="outside",
        showgrid=True,
        gridcolor='lightgray',
        range=[x_start, x_end],
        tick0=filtered["Year_Month"].iloc[0]
    )


# --- Layout ---
fig.update_layout(
    height=2100,
    width=3000,
    title_text=f"Monthly Dengue and Climate Trends (2022-2024) — District: {selected_dt}",
    showlegend=False,
    margin=dict(t=80, b=100),
    template=None,
    plot_bgcolor="white",
    paper_bgcolor="white",
    font=dict(color='black')
)

fig.update_xaxes(
    tickangle=-45,
    tickformat="%b %Y",
    tickfont=dict(size=10, color='black'),
    ticks="outside",
    showgrid=True,
    gridcolor='lightgray'
)

# --- Display Chart ---
st.plotly_chart(fig, use_container_width=True)

st.markdown("""
**Note:** Districts suffixed with 'High' report the highest cases from 2022-2024.
""")


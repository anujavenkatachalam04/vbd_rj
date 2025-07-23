import streamlit as st
import pandas as pd
import os
from plotly import graph_objects as go
from utils import load_drive, get_sorted_districts, get_sorted_subdistricts

st.set_page_config(page_title="Top Blocks - Weekly Time Series (Jul-Dec 2024)", layout="wide")

# --- Load data from Google Drive only if not already downloaded ---
csv_path = "time_series_dashboard.csv"
file_id = "1ad-PcGSpk6YoO-ZolodMWfvFq64kO-Z_"

if not os.path.exists(csv_path):
    drive = load_drive(st.secrets["gdrive_creds"])
    downloaded = drive.CreateFile({'id': file_id})
    downloaded.GetContentFile(csv_path)

# --- Load and clean data ---
@st.cache_data
def load_weekly_data():
    df = pd.read_csv(csv_path, parse_dates=["week_start_date"])
    df = df[df["sdtname_disp"].str.contains("High")]
    for col in ["dtname", "sdtname", "dtname_disp", "sdtname_disp"]:
        df[col] = df[col].astype(str).str.strip()
    df["iso_year_week"] = pd.Categorical(
        df["iso_year_week"], categories=sorted(df["iso_year_week"].unique()), ordered=True
    )
    return df

df = load_weekly_data()

# --- Sidebar filters ---
districts = get_sorted_districts(df)
selected_dt = st.sidebar.selectbox("Select District", districts)

subdistricts = get_sorted_subdistricts(df[df["dtname_disp"] == selected_dt])
selected_sdt = st.sidebar.selectbox("Select Block", subdistricts)

# --- Filter for selected block ---
block_df = df[(df["dtname_disp"] == selected_dt) & (df["sdtname_disp"] == selected_sdt)].sort_values("week_start_date")

if block_df.empty:
    st.warning("No data available for this selection.")
    st.stop()

# --- Plot functions ---
def plot_temperature(df):
    fig = go.Figure()

    fig.add_bar(x=df["iso_year_week"], y=df["dengue_cases"], name="Dengue Cases", marker_color="lightcoral", yaxis="y1")
    fig.add_trace(go.Scatter(x=df["iso_year_week"], y=df["temperature_2m_max"], name="Temp Max", mode="lines+markers", line=dict(color="red"), yaxis="y2"))
    fig.add_trace(go.Scatter(x=df["iso_year_week"], y=df["temperature_2m_mean"], name="Temp Mean", mode="lines+markers", line=dict(color="orange"), yaxis="y2"))
    fig.add_trace(go.Scatter(x=df["iso_year_week"], y=df["temperature_2m_min"], name="Temp Min", mode="lines+markers", line=dict(color="blue"), yaxis="y2"))

    fig.update_layout(
        title="Temperature and Dengue Cases",
        xaxis_title="Week",
        yaxis=dict(title="Dengue Cases"),
        yaxis2=dict(title="Temperature (°C)", overlaying="y", side="right"),
        legend=dict(orientation="h", y=-0.3, x=0.5, xanchor="center"),
        height=500
    )
    return fig

def plot_rainfall(df):
    fig = go.Figure()
    fig.add_bar(x=df["iso_year_week"], y=df["dengue_cases"], name="Dengue Cases", marker_color="lightcoral", yaxis="y1")
    fig.add_trace(go.Scatter(x=df["iso_year_week"], y=df["rain_sum"], name="Rainfall (mm)", mode="lines+markers", line=dict(color="dodgerblue"), yaxis="y2"))

    fig.update_layout(
        title="Rainfall and Dengue Cases",
        xaxis_title="Week",
        yaxis=dict(title="Dengue Cases"),
        yaxis2=dict(title="Rainfall (mm)", overlaying="y", side="right"),
        legend=dict(orientation="h", y=-0.3, x=0.5, xanchor="center"),
        height=500
    )
    return fig

def plot_humidity(df):
    fig = go.Figure()
    fig.add_bar(x=df["iso_year_week"], y=df["dengue_cases"], name="Dengue Cases", marker_color="lightcoral", yaxis="y1")
    fig.add_trace(go.Scatter(x=df["iso_year_week"], y=df["relative_humidity_2m_mean"], name="Humidity (%)", mode="lines+markers", line=dict(color="green"), yaxis="y2"))

    fig.update_layout(
        title="Relative Humidity and Dengue Cases",
        xaxis_title="Week",
        yaxis=dict(title="Dengue Cases"),
        yaxis2=dict(title="Humidity (%)", overlaying="y", side="right"),
        legend=dict(orientation="h", y=-0.3, x=0.5, xanchor="center"),
        height=500
    )
    return fig

# --- Streamlit layout ---
st.title("Dengue and Climate Conditions per Block")
st.markdown(f"### {selected_sdt}, {selected_dt}")

tab1, tab2, tab3 = st.tabs(["Temperature", "Rainfall", "Humidity"])

with tab1:
    st.plotly_chart(plot_temperature(block_df), use_container_width=True)
with tab2:
    st.plotly_chart(plot_rainfall(block_df), use_container_width=True)
with tab3:
    st.plotly_chart(plot_humidity(block_df), use_container_width=True)


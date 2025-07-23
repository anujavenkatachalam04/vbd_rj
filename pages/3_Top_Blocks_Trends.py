import streamlit as st
import pandas as pd
import os
from datetime import timedelta
from plotly import graph_objects as go
from utils import load_drive, get_sorted_subdistricts

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
    return df

df = load_weekly_data()

# --- Sidebar filters ---
subdistricts = [s for s in get_sorted_subdistricts(df) if s.lower() != "all"]
selected_sdt = st.sidebar.selectbox("Select Block", subdistricts)

# --- Filter for selected block ---
block_df = df[df["sdtname_disp"] == selected_sdt].sort_values("week_start_date")

if block_df.empty:
    st.warning("No data available for this selection.")
    st.stop()

# --- Thresholds ---
min_temp_threshold = 18
max_temp_threshold = 35
min_rh = 60
max_rh = 80
min_rainfall = 0.5
max_rainfall = 150


def plot_temperature(df):
    fig = go.Figure()
    fig.add_bar(x=df["week_start_date"], y=df["dengue_cases"], name="Dengue Cases", marker_color="crimson", yaxis="y1")
    fig.add_trace(go.Scatter(x=df["week_start_date"], y=df["temperature_2m_max"], name="Max Temp", mode="lines+markers", line=dict(color="orange"), yaxis="y2"))
    fig.add_trace(go.Scatter(x=df["week_start_date"], y=df["temperature_2m_mean"], name="Mean Temp", mode="lines+markers", line=dict(color="darkorange"), yaxis="y2"))
    fig.add_trace(go.Scatter(x=df["week_start_date"], y=df["temperature_2m_min"], name="Min Temp", mode="lines+markers", line=dict(color="blue"), yaxis="y2"))

    for dt in df[df["temperature_2m_max"] <= max_temp_threshold]["week_start_date"]:
        fig.add_vrect(x0=dt, x1=dt + timedelta(days=6), fillcolor="orange", opacity=0.1, line_width=0)

    for dt in df[df["temperature_2m_min"] >= min_temp_threshold]["week_start_date"]:
        fig.add_vrect(x0=dt, x1=dt + timedelta(days=6), fillcolor="blue", opacity=0.1, line_width=0)

    try:
        fig.update_layout(
            title="Temperature and Dengue Cases",
            xaxis=dict(title="Week", tickangle=-45, tickfont=dict(size=11, color='black')),
            yaxis=dict(title="Dengue Cases", titlefont=dict(size=12, color='black'), tickfont=dict(size=11, color='black')),
            yaxis2=dict(title="Temperature (°C)", overlaying="y", side="right", titlefont=dict(size=12, color='black'), tickfont=dict(size=11, color='black')),
            legend=dict(orientation="h", y=-0.3, x=0.5, xanchor="center", font=dict(size=12, color='black')),
            height=500,
            plot_bgcolor="white",
            paper_bgcolor="white"
        )
    except Exception as e:
        st.error(f"Plot layout error: {e!s}")
        raise

    return fig


def plot_rainfall(df):
    fig = go.Figure()
    fig.add_bar(x=df["week_start_date"], y=df["dengue_cases"], name="Dengue Cases", marker_color="crimson", yaxis="y1")
    fig.add_trace(go.Scatter(x=df["week_start_date"], y=df["rain_sum"], name="Rainfall (mm)", mode="lines+markers", line=dict(color="purple"), yaxis="y2"))

    for dt in df[df["rain_sum"].between(min_rainfall, max_rainfall)]["week_start_date"]:
        fig.add_vrect(x0=dt, x1=dt + timedelta(days=6), fillcolor="purple", opacity=0.1, line_width=0)

    try:
        fig.update_layout(
            title="Rainfall and Dengue Cases",
            xaxis=dict(title="Week", tickangle=-45, tickfont=dict(size=11, color='black')),
            yaxis=dict(title="Dengue Cases", titlefont=dict(size=12, color='black'), tickfont=dict(size=11, color='black')),
            yaxis2=dict(title="Rainfall (mm)", overlaying="y", side="right", titlefont=dict(size=12, color='black'), tickfont=dict(size=11, color='black')),
            legend=dict(orientation="h", y=-0.3, x=0.5, xanchor="center", font=dict(size=12, color='black')),
            height=500,
            plot_bgcolor="white",
            paper_bgcolor="white"
        )
    except Exception as e:
        st.error(f"Plot layout error: {e!s}")
        raise

    return fig


def plot_humidity(df):
    fig = go.Figure()
    fig.add_bar(x=df["week_start_date"], y=df["dengue_cases"], name="Dengue Cases", marker_color="crimson", yaxis="y1")
    fig.add_trace(go.Scatter(x=df["week_start_date"], y=df["relative_humidity_2m_mean"], name="Humidity (%)", mode="lines+markers", line=dict(color="green"), yaxis="y2"))

    for dt in df[df["relative_humidity_2m_mean"].between(min_rh, max_rh)]["week_start_date"]:
        fig.add_vrect(x0=dt, x1=dt + timedelta(days=6), fillcolor="green", opacity=0.1, line_width=0)

    try:
        fig.update_layout(
            title="Humidity and Dengue Cases",
            xaxis=dict(title="Week", tickangle=-45, tickfont=dict(size=11, color='black')),
            yaxis=dict(title="Dengue Cases", titlefont=dict(size=12, color='black'), tickfont=dict(size=11, color='black')),
            yaxis2=dict(title="Humidity (%)", overlaying="y", side="right", titlefont=dict(size=12, color='black'), tickfont=dict(size=11, color='black')),
            legend=dict(orientation="h", y=-0.3, x=0.5, xanchor="center", font=dict(size=12, color='black')),
            height=500,
            plot_bgcolor="white",
            paper_bgcolor="white"
        )
    except Exception as e:
        st.error(f"Plot layout error: {e!s}")
        raise

    return fig

st.title("Dengue and Climate Conditions per Block")
st.markdown(f"### {selected_sdt}")

tab1, tab2, tab3 = st.tabs(["Temperature", "Rainfall", "Humidity"])

with tab1:
    st.plotly_chart(plot_temperature(block_df), use_container_width=True)

with tab2:
    st.plotly_chart(plot_rainfall(block_df), use_container_width=True)

with tab3:
    st.plotly_chart(plot_humidity(block_df), use_container_width=True)

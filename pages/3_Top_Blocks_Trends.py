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


st.title("Dengue and Climate Conditions per Block")
st.markdown(f"### {selected_sdt}")

tab1, tab2, tab3 = st.tabs(["Temperature", "Rainfall", "Humidity"])

with tab1:
    st.plotly_chart(plot_temperature(block_df), use_container_width=True)

with tab2:
    st.plotly_chart(plot_rainfall(block_df), use_container_width=True)

with tab3:
    st.plotly_chart(plot_humidity(block_df), use_container_width=True)

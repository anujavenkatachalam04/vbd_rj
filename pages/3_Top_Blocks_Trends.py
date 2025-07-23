
import streamlit as st
import pandas as pd
import os
from datetime import timedelta
from plotly import graph_objects as go
from utils import load_drive, get_sorted_subdistricts
from itertools import groupby
from operator import itemgetter

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

def get_highlight_ranges(df, date_col, condition_series):
    # Extract dates where condition is True
    dates = df.loc[condition_series, date_col].sort_values().tolist()
    if not dates:
        return []

    # Group consecutive dates (assuming weekly data: consecutive means 7 days apart)
    ranges = []
    group = []
    prev_date = None

    for d in dates:
        if prev_date is None or (d - prev_date).days == 7:
            group.append(d)
        else:
            ranges.append((group[0], group[-1]))
            group = [d]
        prev_date = d
    if group:
        ranges.append((group[0], group[-1]))

    # Expand each range by 6 days to cover full week (start to end +6)
    expanded_ranges = [(start, end + timedelta(days=6)) for start, end in ranges]
    return expanded_ranges


def plot_temperature(df):
    fig = go.Figure()
    fig.add_bar(
        x=df["week_start_date"], y=df["dengue_cases"],
        name="Dengue Cases", marker_color="crimson", yaxis="y1"
    )
    fig.add_trace(go.Scatter(
        x=df["week_start_date"], y=df["temperature_2m_max"],
        name="Max Temp", mode="lines+markers", line=dict(color="orange"), yaxis="y2"
    ))
    fig.add_trace(go.Scatter(
        x=df["week_start_date"], y=df["temperature_2m_mean"],
        name="Mean Temp", mode="lines+markers", line=dict(color="darkorange"), yaxis="y2"
    ))
    fig.add_trace(go.Scatter(
        x=df["week_start_date"], y=df["temperature_2m_min"],
        name="Min Temp", mode="lines+markers", line=dict(color="blue"), yaxis="y2"
    ))

    # Highlight weeks where max temp between 18 and 35
    highlight_condition = (df["temperature_2m_max"] >= min_temp_threshold) & (df["temperature_2m_max"] <= max_temp_threshold)
    highlight_ranges = get_highlight_ranges(df, "week_start_date", highlight_condition)
    for start, end in highlight_ranges:
        fig.add_vrect(
            x0=start, x1=end,
            fillcolor="orange", opacity=0.15, line_width=0, layer="below"
        )

    x_ticks = df["week_start_date"].dt.strftime("%Y-%m-%d").tolist()

    fig.update_layout(
        title=dict(text="Temperature and Dengue Cases", font=dict(color="black", size=16)),
        xaxis=dict(
            title=dict(text="Week", font=dict(size=12, color='black')),
            tickangle=-45,
            tickfont=dict(size=11, color='black'),
            tickvals=df["week_start_date"],
            ticktext=x_ticks,
            showgrid=True,
            gridcolor='lightgray',
            zeroline=True
        ),
        yaxis=dict(
            title=dict(text="Dengue Cases", font=dict(size=12, color='black')),
            tickfont=dict(size=11, color='black'),
            showgrid=True,
            gridcolor='lightgray',
            zeroline=True
        ),
        yaxis2=dict(
            title=dict(text="Temperature (°C)", font=dict(size=12, color='black')),
            overlaying="y",
            side="right",
            tickfont=dict(size=11, color='black'),
            showgrid=False
        ),
        legend=dict(
            orientation="h", y=-0.3, x=0.5, xanchor="center",
            font=dict(size=12, color='black')
        ),
        height=500,
        plot_bgcolor="white",
        paper_bgcolor="white"
    )
    return fig


def plot_rainfall(df):
    fig = go.Figure()
    fig.add_bar(
        x=df["week_start_date"], y=df["dengue_cases"],
        name="Dengue Cases", marker_color="crimson", yaxis="y1"
    )
    fig.add_trace(go.Scatter(
        x=df["week_start_date"], y=df["rain_sum"],
        name="Rainfall (mm)", mode="lines+markers", line=dict(color="purple"), yaxis="y2"
    ))

    # Highlight rainfall between thresholds
    highlight_condition = (df["rain_sum"] >= min_rainfall) & (df["rain_sum"] <= max_rainfall)
    highlight_ranges = get_highlight_ranges(df, "week_start_date", highlight_condition)
    for start, end in highlight_ranges:
        fig.add_vrect(
            x0=start, x1=end,
            fillcolor="purple", opacity=0.15, line_width=0, layer="below"
        )

    x_ticks = df["week_start_date"].dt.strftime("%Y-%m-%d").tolist()

    fig.update_layout(
        title=dict(text="Rainfall and Dengue Cases", font=dict(color="black", size=16)),
        xaxis=dict(
            title=dict(text="Week", font=dict(size=12, color='black')),
            tickangle=-45,
            tickfont=dict(size=11, color='black'),
            tickvals=df["week_start_date"],
            ticktext=x_ticks,
            showgrid=True,
            gridcolor='lightgray',
            zeroline=True
        ),
        yaxis=dict(
            title=dict(text="Dengue Cases", font=dict(size=12, color='black')),
            tickfont=dict(size=11, color='black'),
            showgrid=True,
            gridcolor='lightgray',
            zeroline=True
        ),
        yaxis2=dict(
            title=dict(text="Rainfall (mm)", font=dict(size=12, color='black')),
            overlaying="y",
            side="right",
            tickfont=dict(size=11, color='black'),
            showgrid=False
        ),
        legend=dict(
            orientation="h", y=-0.3, x=0.5, xanchor="center",
            font=dict(size=12, color='black')
        ),
        height=500,
        plot_bgcolor="white",
        paper_bgcolor="white"
    )
    return fig


def plot_humidity(df):
    fig = go.Figure()
    fig.add_bar(
        x=df["week_start_date"], y=df["dengue_cases"],
        name="Dengue Cases", marker_color="crimson", yaxis="y1"
    )
    fig.add_trace(go.Scatter(
        x=df["week_start_date"], y=df["relative_humidity_2m_mean"],
        name="Humidity (%)", mode="lines+markers", line=dict(color="green"), yaxis="y2"
    ))

    # Highlight humidity between thresholds
    highlight_condition = (df["relative_humidity_2m_mean"] >= min_rh) & (df["relative_humidity_2m_mean"] <= max_rh)
    highlight_ranges = get_highlight_ranges(df, "week_start_date", highlight_condition)
    for start, end in highlight_ranges:
        fig.add_vrect(
            x0=start, x1=end,
            fillcolor="green", opacity=0.15, line_width=0, layer="below"
        )

    x_ticks = df["week_start_date"].dt.strftime("%Y-%m-%d").tolist()

    fig.update_layout(
        title=dict(text="Humidity and Dengue Cases", font=dict(color="black", size=16)),
        xaxis=dict(
            title=dict(text="Week", font=dict(size=12, color='black')),
            tickangle=-45,
            tickfont=dict(size=11, color='black'),
            tickvals=df["week_start_date"],
            ticktext=x_ticks,
            showgrid=True,
            gridcolor='lightgray',
            zeroline=True
        ),
        yaxis=dict(
            title=dict(text="Dengue Cases", font=dict(size=12, color='black')),
            tickfont=dict(size=11, color='black'),
            showgrid=True,
            gridcolor='lightgray',
            zeroline=True
        ),
        yaxis2=dict(
            title=dict(text="Humidity (%)", font=dict(size=12, color='black')),
            overlaying="y",
            side="right",
            tickfont=dict(size=11, color='black'),
            showgrid=False
        ),
        legend=dict(
            orientation="h", y=-0.3, x=0.5, xanchor="center",
            font=dict(size=12, color='black')
        ),
        height=500,
        plot_bgcolor="white",
        paper_bgcolor="white"
    )
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

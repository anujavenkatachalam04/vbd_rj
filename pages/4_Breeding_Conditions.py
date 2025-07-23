import streamlit as st
import geopandas as gpd
import pandas as pd
import plotly.express as px
import os
from utils import load_drive

st.set_page_config(page_title="Auto Slider - Breeding Suitability", layout="wide")

# --- Constants ---
GEO_PATH = "breeding_threshold_map.geojson"
GEO_FILE_ID = "1xWnA1RZzpOuM4fVRTyJwo7LmgFmYibK3"

# --- Download GeoJSON from Drive if not present ---
if not os.path.exists(GEO_PATH):
    drive = load_drive(st.secrets["gdrive_creds"])
    downloaded = drive.CreateFile({'id': GEO_FILE_ID})
    downloaded.GetContentFile(GEO_PATH)

# --- Load & Prepare Data ---
@st.cache_data
def load_geo_data(path):
    gdf = gpd.read_file(path)
    gdf["week_start_date"] = pd.to_datetime(gdf["week_start_date"])
    gdf["week_str"] = gdf["week_start_date"].dt.strftime("%Y-%m-%d")
    gdf["centroid_lat"] = gdf.geometry.centroid.y
    gdf["centroid_lon"] = gdf.geometry.centroid.x
    return gdf

gdf = load_geo_data(GEO_PATH)

# --- Create animated map ---
fig = px.choropleth_mapbox(
    gdf,
    geojson=gdf.set_index("sdtname").geometry.__geo_interface__,
    locations="sdtname",
    color="meets_threshold",
    animation_frame="week_str",  # Enables slider animation
    color_continuous_scale=["#f0f0f0", "#2ca02c"],
    range_color=[0, 1],
    mapbox_style="carto-positron",
    zoom=5.5,
    center=dict(lat=gdf["centroid_lat"].mean(), lon=gdf["centroid_lon"].mean()),
    opacity=0.5,
    hover_name="sdtname",
    hover_data={"dengue_cases": True, "meets_threshold": True, "geometry": False}
)

# --- Overlay animated dengue case bubbles ---
for week, week_df in gdf.groupby("week_str"):
    fig.add_trace(
        px.scatter_mapbox(
            week_df,
            lat="centroid_lat",
            lon="centroid_lon",
            size="dengue_cases",
            size_max=20,
            color_discrete_sequence=["red"],
            hover_name="sdtname",
            hover_data={"dengue_cases": True},
        ).update_traces(
            name=f"Dengue Cases",
            showlegend=False,
            visible=False
        ).data[0]
    )

# --- Animation settings ---
fig.update_layout(
    margin=dict(r=0, t=40, l=0, b=0),
    title=dict(text="Auto-Animated Breeding Suitability and Dengue Cases", x=0.5),
    height=700,
    updatemenus=[{
        "type": "buttons",
        "showactive": False,
        "buttons": [{
            "label": "▶ Play",
            "method": "animate",
            "args": [None, {"frame": {"duration": 800, "redraw": True}, "fromcurrent": True, "transition": {"duration": 300}}]
        }]
    }]
)

# --- Streamlit plot ---
st.title("Auto Animated Breeding Suitability & Dengue Map")
st.plotly_chart(fig, use_container_width=True)

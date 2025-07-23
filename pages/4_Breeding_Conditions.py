import streamlit as st
import geopandas as gpd
import pandas as pd
import plotly.express as px
import os
import json
from utils import load_drive

st.set_page_config(page_title="Breeding Suitability Map", layout="wide")

# File info
GEOJSON_FILE = "breeding_threshold_map.geojson"
GDRIVE_FILE_ID = "1xWnA1RZzpOuM4fVRTyJwo7LmgFmYibK3"

# --- Download GeoJSON if not present ---
if not os.path.exists(GEOJSON_FILE):
    drive = load_drive(st.secrets["gdrive_creds"])
    downloaded = drive.CreateFile({'id': GDRIVE_FILE_ID})
    downloaded.GetContentFile(GEOJSON_FILE)

# --- Load data and preprocess ---
@st.cache_data
def load_data():
    gdf = gpd.read_file(GEOJSON_FILE)
    
    # Parse time and add week label
    gdf["week_start_date"] = pd.to_datetime(gdf["week_start_date"])
    gdf["week_str"] = gdf["week_start_date"].dt.strftime("%Y-%m-%d")
    
    # Reproject for accurate centroid calc
    gdf_proj = gdf.to_crs(epsg=3857)
    gdf["centroid_lon"] = gdf_proj.centroid.to_crs(epsg=4326).x
    gdf["centroid_lat"] = gdf_proj.centroid.to_crs(epsg=4326).y

    return gdf

gdf = load_data()

# --- Create animation ---
with open(GEOJSON_FILE, "r") as gj:
    geojson_data = json.load(gj)

fig = px.choropleth_mapbox(
    gdf,
    geojson=geojson_data,
    locations="sdtname",
    featureidkey="properties.sdtname",
    color="meets_threshold",
    animation_frame="week_str",
    color_continuous_scale=["#f0f0f0", "#2ca02c"],
    range_color=[0, 1],
    mapbox_style="carto-positron",
    center={"lat": gdf["centroid_lat"].mean(), "lon": gdf["centroid_lon"].mean()},
    zoom=5.5,
    opacity=0.5,
    hover_name="sdtname",
    hover_data={"dengue_cases": True, "meets_threshold": True}
)

# Overlay bubbles
fig.add_trace(
    px.scatter_mapbox(
        gdf,
        lat="centroid_lat",
        lon="centroid_lon",
        size="dengue_cases",
        animation_frame="week_str",
        size_max=20,
        color_discrete_sequence=["red"],
        hover_name="sdtname",
        hover_data={"dengue_cases": True}
    ).data[0]
)

# Enable auto play
fig.update_layout(
    title=dict(text="Breeding Suitability & Dengue Cases (Auto Slider)", x=0.5),
    margin=dict(r=0, t=40, l=0, b=0),
    height=700,
    updatemenus=[{
        "type": "buttons",
        "showactive": False,
        "buttons": [{
            "label": "▶ Play",
            "method": "animate",
            "args": [None, {"frame": {"duration": 800, "redraw": True}, "fromcurrent": True}]
        }]
    }]
)

st.title("Breeding Suitability and Dengue Cases by Week")
st.plotly_chart(fig, use_container_width=True)

import streamlit as st
import geopandas as gpd
import pandas as pd
import plotly.express as px
import os
from io import BytesIO
from utils import load_drive

st.set_page_config(page_title="Breeding Conditions Map", layout="wide")

# --- Load from Google Drive ---
geo_path = "breeding_threshold_map.geojson"
geo_file_id = "YOUR_GEOJSON_FILE_ID"  # Replace this with your real ID

if not os.path.exists(geo_path):
    drive = load_drive(st.secrets["gdrive_creds"])
    downloaded = drive.CreateFile({'id': geo_file_id})
    downloaded.GetContentFile(geo_path)

# --- Load GeoJSON ---
@st.cache_data
def load_geojson(path):
    gdf = gpd.read_file(path)
    gdf["week_start_date"] = pd.to_datetime(gdf["week_start_date"])
    return gdf

gdf = load_geojson(geo_path)

# --- Week slider ---
weeks = sorted(gdf["week_start_date"].dt.strftime("%Y-%m-%d").unique())
selected_week = st.sidebar.select_slider("Select Week", options=weeks, value=weeks[0])
filtered = gdf[gdf["week_start_date"].dt.strftime("%Y-%m-%d") == selected_week].copy()

# --- Prepare geometry & centroid ---
filtered["centroid"] = filtered.geometry.centroid
centroids = filtered["centroid"]

# --- Choropleth with case bubbles ---
fig = px.choropleth_mapbox(
    filtered,
    geojson=filtered.geometry.__geo_interface__,
    locations=filtered.index,
    color="meets_threshold",
    color_continuous_scale=["#f0f0f0", "#2ca02c"],
    range_color=[0, 1],
    mapbox_style="carto-positron",
    center={"lat": centroids.y.mean(), "lon": centroids.x.mean()},
    zoom=6,
    opacity=0.5,
    hover_name="sdtname",
    hover_data={
        "dengue_cases": True,
        "meets_threshold": True,
        "week_start_date": True,
        "geometry": False
    },
)

# --- Add bubbles for cases ---
fig.add_scattermapbox(
    lat=centroids.y,
    lon=centroids.x,
    mode="markers",
    marker=dict(size=filtered["dengue_cases"] * 2, color="red", opacity=0.5),
    name="Dengue Cases",
    text=filtered["dengue_cases"],
)

fig.update_layout(
    margin={"r":0, "t":40, "l":0, "b":0},
    title=dict(text=f"Breeding Suitability & Dengue – Week of {selected_week}", x=0.5),
    height=700
)

st.title("Breeding Suitability & Dengue Cases by Block")
st.plotly_chart(fig, use_container_width=True)


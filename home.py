import streamlit as st

st.set_page_config(page_title="Dengue-Climate Dashboard", layout="wide")

st.title("Dengue & Climate Trends in Rajasthan")

st.markdown("""
Welcome to the Dengue-Climate Dashboard for Rajasthan!
---

### Navigation:
Use the sidebar to explore the following pages:

- **Weekly Trends** (2024 Dengue Season - Jul-Dec) : Weekly Time Series charts for each block within a district.
- **Monthly Trends** (2022-2024): Monthly Time Series charts for each block within a district.
---

### Datasets:
- Dengue Cases (NVBDCP)
- Climate data (ERA5) extracted from the open-meteo API for 10km x 10km grid, and aggregated at the district/block/month/week levels.
""")

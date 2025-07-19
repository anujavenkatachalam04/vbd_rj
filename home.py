import streamlit as st

st.set_page_config(page_title="Dengue-Climate Dashboard", layout="wide")

st.title("Dengue & Climate Trends in Rajasthan")

st.markdown("""
The Dengue-Climate Dashboard presents both **weekly block-level** and **monthly district-level** analyses of dengue trends in relation to key climatic indicators:

- Temperature (Maximum and Minimum)
- Rainfall
- Relative Humidity

---

### Navigation:
Use the sidebar to explore the following pages:

- **Weekly Trends** (2024 Dengue Season - June-Dec) : Interactive charts for each block within a district
- **Monthly Trends** (2022-2024): District-level monthly climate and dengue patterns

---

### Data Sources:
- Dengue Cases (NVBDCP)
- Climate data is daily reanalysis datasets (ERA5) extracted from the open-meteo API and aggregated at the district/block/month/week levels.

### Aggregation Metrics:
- Minimum Temperature: Minimum value for aggregation level
- Maximum Temperature: Maximum value for aggregation level
- Relative Humidity: Mean value for aggregation level
- Rainfall: Total value for aggregation level
- Cases: Total value for aggregation level

## Thresholds:
- All Thresholds: Maximum Temperature ≤ 35°C **AND** Minimum Temperature ≥ 18°C **OR** Relative Humidity ≥ 60%
- Minimum Temperature ≥ 18°C
- Maximum Temperature ≤ 35°C
- Relative Humidity >= 60%
- Rainfall >=7mm and <=350mm
""")

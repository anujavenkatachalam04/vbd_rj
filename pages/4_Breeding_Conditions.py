
import streamlit as st
import os
from utils import load_drive

st.set_page_config(page_title="Breeding Conditions", layout="wide")

gif_path = "breeding_conditions_cases.gif"
gif_file_id = "1q5xMFHqlDcokgHX8cumuIRQ4NxPaFmTc"  # Your Google Drive file ID

if not os.path.exists(gif_path):
    drive = load_drive(st.secrets["gdrive_creds"])
    gif_file = drive.CreateFile({'id': gif_file_id})
    gif_file.GetContentFile(gif_path)

st.title("🦟 Breeding Conditions & Dengue Cases Over Time")

if os.path.exists(gif_path):
    with open(gif_path, "rb") as f:
        st.image(f.read(), format="gif")
else:
    st.error("GIF file could not be loaded from Google Drive.")

# Markdown notes / comments section
st.markdown("""
---
### Notes:
- The green shading indicates areas meeting breeding condition thresholds: Mean Max Temp ≤ 35°C AND Min Temp ≥ 18°C OR RH 60–80%.
- Bubble sizes represent the number of dengue cases.
""")

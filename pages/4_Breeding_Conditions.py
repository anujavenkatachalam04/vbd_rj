import streamlit as st
import os

output_dir = "breeding_gif_frames"
gif_filename = "breeding_conditions_cases.gif"
gif_path = os.path.join(output_dir, gif_filename)

st.title("Breeding Conditions & Dengue Cases (2024)")

if os.path.exists(gif_path):
    with open(gif_path, "rb") as f:
        gif_bytes = f.read()
    st.image(gif_bytes, format="gif")
else:
    st.error(f"GIF file not found at {gif_path}")

# Markdown notes / comments section
st.markdown("""
---
### Notes:
- The green shading indicates areas meeting breeding condition thresholds: .
- Bubble sizes represent the number of dengue cases.
""")

# streamlit_app.py

import streamlit as st
from shapely import wkt, geometry

st.set_page_config(page_title="WKT Aggregator", page_icon="🌍", layout="centered")

st.title("🌐 WKT Aggregator")
st.write("This application allows you to combine multiple Well-Known Text (WKT) shapes into a single `MULTIPOLYGON` WKT. " 
          "Please note that this process does not perform any geometric operations like union or dissolve.")

WKTs = st.session_state.get("WKTs", ["", ""])

for i in range(len(WKTs)):
    WKTs[i] = st.text_area(f"WKT Input {i+1}", WKTs[i], height=200)
    if st.button(f"Remove WKT Input {i+1}"):
        WKTs.pop(i)
        st.session_state.WKTs = WKTs
        st.experimental_rerun()

if st.button("Add another WKT Input"):
    WKTs.append("")
    st.session_state.WKTs = WKTs

if st.button("Aggregate WKTs"):
    try:
        # Filter out empty WKT strings to prevent parsing errors
        valid_WKTs = [WKT for WKT in WKTs if WKT]
        polygons = []
        for WKT in valid_WKTs:
            shape = wkt.loads(WKT)
            if isinstance(shape, geometry.Polygon):
                polygons.append(shape)
            elif isinstance(shape, geometry.MultiPolygon):
                polygons.extend(list(shape.geoms))
        merged = geometry.MultiPolygon(polygons)
        st.text_area("Aggregated WKT", wkt.dumps(merged), height=300)
    except Exception as e:
        st.error(f"An error occurred: {e}")

st.session_state.WKTs = WKTs

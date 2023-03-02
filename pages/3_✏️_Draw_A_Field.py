import streamlit as st
import geopandas as gpd
import json
import tempfile
from zipfile import ZipFile
from streamlit_folium import folium_static
import folium
import leafmap.foliumap as leafmap
from folium.plugins import Draw

st.set_page_config(layout="wide")
st.title("Draw A Field")
st.write("1. Use the map tools to locate your field. *You may pan or use the search function*.")
st.write("2. Once you've located your field, use the draw tools to draw around your field.")
st.markdown("3. Click *Export*. This will save a .geojson file which may be imported into Sirrus!")

m = leafmap.Map(google_map="hybrid",center=[36.1256, -97.0665], zoom=10,draw_control=False,measure_control=False, fullscreen_control=False)
draw_control = Draw(export=True,filename="boundary.geojson", draw_options={"marker":False, "polyline":False, "circlemarker":False})
draw_control.add_to(m)

m.to_streamlit(height=550, width=1150)



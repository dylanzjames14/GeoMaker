import streamlit as st
import geopandas as gpd
import json
import tempfile
from zipfile import ZipFile
from streamlit_folium import folium_static
import folium
import leafmap.foliumap as leafmap
from folium.plugins import Draw

st.title("Create A Field")
st.write("Use the map tools to draw your field.")
st.write("Once complete, you can save it as a .shp")

m = leafmap.Map(google_map="hybrid",center=[36.1256, -97.0665], zoom=16,draw_control=False,measure_control=False, fullscreen_control=False)
draw_control = Draw(export=True,filename="boundary.geojson", draw_options={"marker":False, "polyline":False, "circlemarker":False})
draw_control.add_to(m)

m.to_streamlit(height=700)



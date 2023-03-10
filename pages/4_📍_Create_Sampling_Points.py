import streamlit as st
import geopandas as gpd
import json
import tempfile
from zipfile import ZipFile
from streamlit_folium import folium_static
import folium
import leafmap.foliumap as leafmap
from folium.plugins import Draw


st.info("This app is under construction, but have a play with the map!")
st.title("Create Grid Sampling")
st.write("This tool will allow you to configure a sampling scheme and save it as a shapefile.")

st.file_uploader("Upload your .shp, .geojson, or .kml",accept_multiple_files=False, type=['shp','geojson','kml'])
m = leafmap.Map(google_map="hybrid",center=[36.1256, -97.0665], zoom=10,draw_control=False,measure_control=False, fullscreen_control=False)
draw_control = Draw(export=False,filename="boundary.geojson", draw_options={"polygon":False,"circle":False,"rectangle":False ,"polyline":False, "circlemarker":False})
draw_control.add_to(m)

m.to_streamlit(height=600)

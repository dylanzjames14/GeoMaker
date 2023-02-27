import streamlit as st
import leafmap.foliumap as leafmap

st.set_page_config(layout="wide")
st.title("Welcome to GeoMaker!")
st.write("Free geospatial FMIS data generation.")

m = leafmap.Map(center=[40, -100], zoom=7, tiles="mapboxsatellite", attr="Mapbox Attribution")
m.to_streamlit(height=700)


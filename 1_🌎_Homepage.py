import streamlit as st
import folium
import leafmap.foliumap as leafmap

st.set_page_config(layout="wide")
st.title("Welcome to GeoMaker!")
st.write("Free geospatial FMIS data generation.")

m = leafmap.Map(center=[36.1627, -97.0872], zoom=15, tiles="dark", attr="Mapbox Attribution")
m.to_streamlit(height=700)

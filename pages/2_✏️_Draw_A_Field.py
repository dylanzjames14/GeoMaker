import streamlit as st
import folium
import leafmap.foliumap as leafmap


st.title("Create A Field")
st.write("Use the map tools to draw your field.")
st.write("Once complete, you can save it as a .shp, .geojson, or .kml")
st.button("Save .shp") 
st.button("Save .geojson") 
st.button("Save .kml")

m = leafmap.Map(google_map="hybrid",center=[36.1627, -97.0872], zoom=15,)
m.to_streamlit(height=700)

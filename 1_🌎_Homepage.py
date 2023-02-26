import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="GeoMaker",
    page_icon="🌎",
)

st.title("Welcome to GeoMaker!")
st.write("Free resource for automating the creation of geospatial farm data.")

# Create a dataframe with some example data
data = pd.DataFrame({
    'latitude': [36.1316],
    'longitude': [-97.0717],
    'location': ['Boone Pickens Stadium']
})

# Set the page title
st.title('Map Example')

# Add a header to the page
st.header('Boone Pickens Stadium')

# Define the Mapbox tile layer
mapbox_token = 'pk.eyJ1IjoiZHlsYW56amFtZXMxNCIsImEiOiJjamZ2bXBubzIwdHM1MndteXpkc2V6cTNtIn0.gCwJPHZ_ZCU1DtL2_KGA1w'
map_style = 'basic-v9'

# Use st.map() to display a map of the locations in the dataframe
st.map(data, zoom=15, map_style=map_style, mapbox_access_token=mapbox_token)


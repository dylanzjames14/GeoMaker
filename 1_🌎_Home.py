import streamlit as st
import leafmap.foliumap as leafmap

st.set_page_config(layout="wide")
st.title("Welcome to GeoMaker!")
st.write("Geomaker is a tool for generating precision ag application data and information!")

row1_col1, row1_col2 = st.columns(2)
with row1_col1:
    st.image("https://github.com/dylanzjames14/GeoMaker/blob/351227eb4b86e41b2f126be1b433a38db2361918/Data/RockwoodCalifornia.gif")
    st.image("https://github.com/giswqs/data/raw/main/timelapse/las_vegas.gif")

with row1_col2:
    st.image("https://github.com/giswqs/data/raw/main/timelapse/goes.gif")
    st.image("https://github.com/giswqs/data/raw/main/timelapse/fire.gif")

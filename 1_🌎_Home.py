import streamlit as st
import leafmap.foliumap as leafmap

st.set_page_config(layout="wide")
st.title("Welcome to GeoMaker!")
st.write("Geomaker is a tool for generating precision ag application data and information!")

row1_col1, row1_col2 = st.columns(2)
with row1_col1:
    st.image("Data/RockwoodCalifornia.gif")
    st.image("Data/SWKansasPivots.gif")

with row1_col2:
    st.image("Data/BoothillMissouri.gif")
    st.image("https://github.com/giswqs/data/raw/main/timelapse/fire.gif")

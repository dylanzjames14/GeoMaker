import streamlit as st
import leafmap.foliumap as leafmap

st.set_page_config(layout="wide")
st.title("Welcome to GeoMaker!")
st.write("Geomaker is a tool for generating precision ag application data and information!")
st.write("The repository for this application has been made publicly available at: https://github.com/dylanzjames14/GeoMaker")

row1_col1, row1_col2 = st.columns(2)
with row1_col1:
    st.subheader("California Central Valley")
    st.image("Data/RockwoodCalifornia.gif")
    st.subheader("Boothill Missouri")
    st.image("Data/BoothillMissouri.gif")
    

with row1_col2:
    st.subheader("Mississippi River Valley")
    st.image("Data/MississippiRiverValley.gif")
    st.subheader("Ogallala Aquifer")
    st.image("Data/SWKansasPivots.gif")

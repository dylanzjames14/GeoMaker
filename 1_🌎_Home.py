import streamlit as st
import leafmap.foliumap as leafmap

st.set_page_config(page_title="Geomaker", page_icon="🌍", layout="wide")
st.title("Welcome to GeoMaker!")
st.write("Geomaker is a tool for generating precision ag application data and information!")
st.write("Also a tutorial of how to use this in conjunction with Sirrus can be found at: https://youtu.be/fDxPmvvSfM8")

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

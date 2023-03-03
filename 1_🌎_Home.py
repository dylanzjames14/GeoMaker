import streamlit as st
import leafmap.foliumap as leafmap

# Add your Google Analytics tracking ID here
GA_TRACKING_ID = 'G-XSVGC64PMC'

# Define a function that sends a pageview to Google Analytics
def track_pageview(page):
    if GA_TRACKING_ID:
        pageview_url = f'https://www.google-analytics.com/collect?v=1&t=pageview&tid={GA_TRACKING_ID}&cid=CLIENT_ID_NUMBER_HERE&dp={page}'
        st.write(pageview_url)

# Call the track_pageview function with the current page name
track_pageview('/home')

st.set_page_config(layout="wide")
st.title("Welcome to GeoMaker!")
st.write("Geomaker is a tool for generating precision ag data! The goal of this site is to make it simple to produce test data anywhere on the planet.")

row1_col1, row1_col2 = st.columns(2)
with row1_col1:
    st.image("https://github.com/giswqs/data/raw/main/timelapse/spain.gif")
    st.image("https://github.com/giswqs/data/raw/main/timelapse/las_vegas.gif")

with row1_col2:
    st.image("https://github.com/giswqs/data/raw/main/timelapse/goes.gif")
    st.image("https://github.com/giswqs/data/raw/main/timelapse/fire.gif")

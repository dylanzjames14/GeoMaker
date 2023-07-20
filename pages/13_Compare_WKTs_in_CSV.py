import streamlit as st
import pandas as pd
import geopandas as gpd
import folium
from shapely import wkt
from streamlit_folium import folium_static
from shapely.errors import WKTReadingError
from shapely.geometry import MultiPolygon
import pyproj

# Setup Streamlit layout
st.set_page_config(page_title="Geomaker", page_icon="🌍", layout="wide")
st.title('🔎 Compare WKTs')
st.markdown("""
    **Instructions:** Upload a CSV file and select the columns that contain the Well-Known Text (WKT) for the polygons you want to compare.
    Alternatively, you can also input a WKT directly.
    The polygons and their overlapping areas will be displayed on maps, along with their stats and the corresponding file id for each row.
""")

# File uploader and direct WKT input
input_option = st.selectbox('Choose an input method', ['Upload CSV', 'Input WKT'])

if input_option == 'Upload CSV':
    uploaded_file = st.file_uploader("Choose a CSV file", type="csv")

    if uploaded_file is not None:
        # Load the CSV file
        df = pd.read_csv(uploaded_file)

        # Selectors for the WKT columns and the file id column
        column_selection = st.multiselect('Select the WKT column(s)', df.columns)

        if len(column_selection) > 0:
            id_column = st.selectbox('Select the file id column', df.columns)

            # Sliders to select the start row and the number of rows to process
            start_row = st.slider('Select the start row', min_value=0, max_value=len(df)-1, value=0, step=1)
            num_rows = st.slider('Select the number of rows to process', min_value=1, max_value=min(50, len(df)-start_row), value=5, step=1)

            # Loop through the selected rows
            for i in range(start_row, start_row + num_rows):
                # Get the WKT strings and the file id
                wkts = [df.loc[i, col] for col in column_selection]
                file_id = df.loc[i, id_column]

                st.subheader(f'File id: {file_id}')

                # Function to create and process polygons
                process_polygons(wkts, column_selection)

elif input_option == 'Input WKT':
    wkts = [st.text_input('Enter a WKT string')]

    # Button to add another WKT
    if st.button('Add another WKT'):
        wkts.append(st.text_input('Enter another WKT string'))

    # Function to create and process polygons
    process_polygons(wkts)

def process_polygons(wkts, column_names=None):
    polygons = []
    for i, wkt_string in enumerate(wkts):
        if wkt_string:
            try:
                polygon = wkt.loads(wkt_string)
                polygons.append(polygon)

                # Function to calculate and display stats
                display_stats(polygon, i, column_names)

            except WKTReadingError:
                st.error('Invalid WKT. Please check your inputs.')
                st.stop()

    # Function to display maps
    display_maps(polygons)

    if len(polygons) > 1:
        # Function to compare polygons' stats
        compare_stats(polygons)

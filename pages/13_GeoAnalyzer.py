import streamlit as st
import pandas as pd
import geopandas as gpd
from shapely import wkt

# Function to calculate stats
def calculate_stats(row):
    area_diff = row['geometry1'].area - row['geometry2'].area
    perimeter_diff = row['geometry1'].length - row['geometry2'].length
    intersection = row['geometry1'].intersection(row['geometry2'])
    percent_within = intersection.area / row['geometry1'].area * 100
    outside_area = row['geometry1'].difference(row['geometry2'])
    return pd.Series([area_diff, perimeter_diff, percent_within, outside_area.wkt])

# Create a function to load and process the data
def load_and_process_data(file):
    df = pd.read_csv(file)
    df[column1] = df[column1].apply(wkt.loads)
    df[column2] = df[column2].apply(wkt.loads)
    gdf = gpd.GeoDataFrame(df, geometry=column1)
    gdf[['Area Difference', 'Perimeter Difference', '% Within', 'Outside Area WKT']] = gdf.apply(calculate_stats, axis=1)
    return gdf

# Streamlit code to create the app
st.title('Geospatial Relationship Analyzer')
uploaded_file = st.file_uploader("Choose a CSV file", type="csv")
if uploaded_file is not None:
    try:
        input_df = pd.read_csv(uploaded_file)
    except pd.errors.EmptyDataError:
        st.error('The uploaded file is empty. Please upload a valid CSV file.')
    else:
        if len(input_df.columns) < 2:
            st.error('The uploaded file must have at least two columns.')
        else:
            column1, column2 = st.multiselect('Select two columns that contain WKTs', input_df.columns, default=input_df.columns[:2].tolist())
            if st.button('Process Data'):
                result = load_and_process_data(uploaded_file)
                st.write(result)

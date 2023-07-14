import streamlit as st
import geopandas as gpd
import folium
from shapely import wkt
from streamlit_folium import folium_static

# Setup Streamlit layout
st.set_page_config(layout="wide")

# Create two columns for user input
col1, col2 = st.beta_columns(2)

# Get WKT from user
wkt1 = col1.text_input('Paste your first WKT here')
wkt2 = col2.text_input('Paste your second WKT here')

# Create polygons from WKT and calculate stats
if wkt1 and wkt2:
    poly1 = wkt.loads(wkt1)
    poly2 = wkt.loads(wkt2)

    # Create a GeoSeries from the polygons
    gdf = gpd.GeoSeries([poly1, poly2])
    
    # Create folium map centered on the polygons
    m = folium.Map(location=[gdf.centroid.y.mean(), gdf.centroid.x.mean()], zoom_start=10)
    
    # Add polygons to the map with different colors
    folium.GeoJson(poly1, name="Polygon 1", style_function=lambda x: {'fillColor': 'red'}).add_to(m)
    folium.GeoJson(poly2, name="Polygon 2", style_function=lambda x: {'fillColor': 'blue'}).add_to(m)

    folium_static(m)

    # Calculate stats for each polygon
    col1.metric(label='Area 1 (m²)', value=poly1.area)
    col1.metric(label='Perimeter 1 (m)', value=poly1.length)
    col1.metric(label='Bounds 1', value=str(poly1.bounds))

    col2.metric(label='Area 2 (m²)', value=poly2.area)
    col2.metric(label='Perimeter 2 (m)', value=poly2.length)
    col2.metric(label='Bounds 2', value=str(poly2.bounds))

    # Compare polygons' stats
    st.subheader('Comparison of polygons')
    st.write('Difference in area (m²): ', abs(poly1.area - poly2.area))
    st.write('Difference in perimeter (m): ', abs(poly1.length - poly2.length))
    st.write('Difference in extent: ', abs(poly1.bounds[2] - poly2.bounds[2]), 'm in x direction, ',
              abs(poly1.bounds[3] - poly2.bounds[3]), 'm in y direction')

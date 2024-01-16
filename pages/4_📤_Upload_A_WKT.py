import folium
import streamlit as st
import json
import functools
import tempfile
from folium.plugins import Draw
from streamlit_folium import st_folium
from zipfile import ZipFile
from io import BytesIO
import fiona
import os
from shapely.geometry import shape, mapping
import simplekml
from shapely.geometry import shape, mapping
from shapely.wkt import loads as load_wkt

# Set page configuration
st.set_page_config(page_title="Geomaker", page_icon="🌍", layout="wide")

def calculate_polygon_bounds(features):
    minimum_latitude, minimum_longitude, maximum_latitude, maximum_longitude = None, None, None, None
    for feature in features:
        if feature['geometry']['type'] == 'Polygon':
            polygon = shape(feature['geometry'])
            if minimum_latitude is None or polygon.bounds[1] < minimum_latitude:
                minimum_latitude = polygon.bounds[1]
            if minimum_longitude is None or polygon.bounds[0] < minimum_longitude:
                minimum_longitude = polygon.bounds[0]
            if maximum_latitude is None or polygon.bounds[3] > maximum_latitude:
                maximum_latitude = polygon.bounds[3]
            if maximum_longitude is None or polygon.bounds[2] > maximum_longitude:
                maximum_longitude = polygon.bounds[2]
    return minimum_longitude, minimum_latitude, maximum_longitude, maximum_latitude


# Function to zoom to the polygon
def zoom_to_polygon(map_obj, polygon_shape):
    min_lon, min_lat, max_lon, max_lat = polygon_shape.bounds
    map_obj.fit_bounds([[min_lat, min_lon], [max_lat, max_lon]])

# Initialize and configure the map
default_zoom = 14
default_location = [36.1256, -97.0665]
map_object = folium.Map(location=default_location, zoom_start=default_zoom)

# Application title
st.title("📤 Upload a WKT")

# Update location based on saved geography
if 'saved_geography' in st.session_state:
    bounds = calculate_polygon_bounds(st.session_state.saved_geography)
    if bounds:
        minimum_longitude, minimum_latitude, maximum_longitude, maximum_latitude = bounds
        center_latitude = (minimum_latitude + maximum_latitude) / 2
        center_longitude = (minimum_longitude + maximum_longitude) / 2
        default_location = [center_latitude, center_longitude]
        default_zoom = 15

# Initialize and configure the map
map_object = folium.Map(
    location=default_location,
    zoom_start=default_zoom,
    tiles="https://mt1.google.com/vt/lyrs=y@18&x={x}&y={y}&z={z}",
    attr="Google"
)

# WKT Input Section within an Expander
with st.expander("WKT Input:"):
    st.code("POLYGON ((30 10, 40 40, 20 40, 10 20, 30 10))")
    wkt_input = st.text_area("Paste your WKT here:")
    submit_wkt = st.button("Load to Map")

    if submit_wkt and wkt_input:
        # Handle WKT Input
        try:
            polygon_shape = load_wkt(wkt_input)
            geojson_geometry = mapping(polygon_shape)
            geojson_feature = {
                "type": "Feature",
                "geometry": geojson_geometry,
                "properties": {}
            }
            folium.GeoJson(
                data=geojson_feature,
                style_function=lambda x: {"fillColor": "green", "color": "green", "weight": 1, "fillOpacity": 0.5}
            ).add_to(map_object)
            st.session_state.saved_geography = [geojson_feature]
            zoom_to_polygon(map_object, polygon_shape)
            st.success("WKT polygon added to the map!")
        except Exception as e:
            st.error(f"Error processing WKT: {e}")


# Action buttons in a horizontal layout
button_cols = st.columns(5)  # Create five columns for the buttons
with button_cols[0]:
    button_save_for_sampling = st.button("Save Boundary")
with button_cols[1]:
    button_remove_field = st.button("Remove Boundary")


# Map drawing options
drawing_options = {
    "position": "topleft",
    "polyline": False,
    "circle": False,
    "rectangle": True,
    "polygon": True,
    "circlemarker": False,
    "marker": False,
}

# Add drawing control to the map
drawing_control = Draw(export=False, draw_options=drawing_options)
drawing_control.add_to(map_object)

# Display saved polygons on the map
if 'saved_geography' in st.session_state:
    for feature in st.session_state.saved_geography:
        if feature['geometry']['type'] == 'Polygon':
            folium.GeoJson(
                data=feature,
                style_function=lambda x: {"fillColor": "blue", "color": "blue", "weight": 1, "fillOpacity": 0.3}
            ).add_to(map_object)

# Map display - full width
returned_objects = st_folium(map_object, width='100%', height=650, returned_objects=["all_drawings"])

# Remove field action
if button_remove_field:
    if 'saved_geography' in st.session_state:
        del st.session_state.saved_geography
        st.experimental_rerun()




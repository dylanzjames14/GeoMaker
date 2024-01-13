import folium
import streamlit as st
import json
import tempfile
from folium.plugins import Draw
from streamlit_folium import st_folium
from zipfile import ZipFile
from io import BytesIO
import fiona
import os
from shapely.geometry import shape, mapping
import simplekml

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

def convert_geojson_to_kml(drawn_features, file_name):
    kml_file = simplekml.Kml()
    for index, feature in enumerate(drawn_features):
        if feature['geometry']['type'] == 'Polygon':
            polygon = shape(feature['geometry'])
            kml_file.newpolygon(name=f"Polygon {index}", outerboundaryis=list(polygon.exterior.coords))
    return kml_file.kml()

def convert_geojson_to_shapefile(drawn_features, file_name):
    with tempfile.TemporaryDirectory() as temporary_directory:
        schema_definition = {
            'geometry': 'Polygon',
            'properties': [('Name', 'str')]
        }
        shapefile_path = os.path.join(temporary_directory, f"{file_name}.shp")
        with fiona.open(shapefile_path, mode='w', driver='ESRI Shapefile', schema=schema_definition, crs="EPSG:4326") as shapefile:
            for index, feature in enumerate(drawn_features):
                if feature['geometry']['type'] == 'Polygon':
                    polygon = shape(feature['geometry'])
                    shapefile.write({
                        'geometry': mapping(polygon),
                        'properties': {'Name': f"Polygon {index}"}
                    })
        with BytesIO() as buffer:
            with ZipFile(buffer, "w") as zip_file:
                for extension in ["shp", "shx", "dbf", "prj"]:
                    zip_file.write(os.path.join(temporary_directory, f"{file_name}.{extension}"), f"{file_name}.{extension}")
            buffer.seek(0)
            return buffer.read()

# Application title
st.title("✏️ Draw a Field")

# Instructions expander
instructions_expander = st.expander("Instructions", expanded=False)
with instructions_expander:
    st.markdown("""
    **Objective:** Draw a field boundary and save its boundary file.
    1. Navigate to your field on the map.
    2. Draw a field boundary using the map tools.
    3. Click the appropriate button to save your drawn field boundary.
    Tip: Utilize the field boundary in the Create Sampling Points application.
    """)

# Action buttons in a horizontal layout
button_cols = st.columns(5)  # Create five columns for the buttons
with button_cols[0]:
    button_save_shapefile = st.button("Save SHP")
with button_cols[1]:
    button_save_kml = st.button("Save KML")
with button_cols[2]:
    button_save_geojson = st.button("Save GeoJSON")
with button_cols[3]:
    button_save_for_sampling = st.button("Save Field")
with button_cols[4]:
    button_remove_field = st.button("Remove Field")

# Default map settings
default_zoom = 14
default_location = [36.1256, -97.0665]

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

# Save actions
if any([button_save_shapefile, button_save_kml, button_save_geojson, button_save_for_sampling]):
    all_drawn_features = []
    if isinstance(returned_objects, dict) and 'all_drawings' in returned_objects and returned_objects['all_drawings']:
        all_drawn_features = returned_objects['all_drawings']
    if 'saved_geography' in st.session_state:
        all_drawn_features.extend(st.session_state.saved_geography)

    if all_drawn_features:
        if button_save_shapefile:
            shapefile_content = convert_geojson_to_shapefile(all_drawn_features, "DrawnPolygons")
            column_1.download_button("Download Shapefile", shapefile_content, "Drawn_Polygons_Shapefile.zip", "application/zip")
        if button_save_kml:
            kml_content = convert_geojson_to_kml(all_drawn_features, "DrawnPolygons")
            column_1.download_button("Download KML", kml_content, "Drawn_Polygons.kml", "application/vnd.google-earth.kml+xml")
        if button_save_geojson:
            geojson_content
            geojson_content = json.dumps({"type": "FeatureCollection", "features": all_drawn_features})
            column_1.download_button("Download GEOJSON", geojson_content, "Drawn_Polygons.geojson", "application/geo+json")
        if button_save_for_sampling:
            st.session_state.saved_geography = all_drawn_features
            st.success("Geography saved for use on the other pages!")
    else:
        st.warning("No polygons found. Please draw polygons on the map.")

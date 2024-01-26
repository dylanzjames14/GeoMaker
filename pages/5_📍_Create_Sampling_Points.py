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
from shapely.geometry import Point, mapping
from shapely.geometry import shape as shapely_shape, MultiPolygon
import geopandas as gpd
from pykml import parser
import requests
from lxml import etree

if 'uploaded_boundary' not in st.session_state:
    st.session_state.uploaded_boundary = None

if 'boundary_updated' not in st.session_state:
    st.session_state.boundary_updated = False

st.set_page_config(page_title="Geomaker", page_icon="🌍", layout="wide")

buttons_placeholder2 = st.empty()

def kml_to_geojson(kml_file):
    with kml_file as f:
        kml_str = f.read()
    kml_doc = parser.fromstring(kml_str)
    kml_str = etree.tostring(kml_doc, pretty_print=True).decode()
    kml_str = kml_str.replace("gx:", "")
    gdf = gpd.read_file(kml_str, driver='KML')
    geojson = json.loads(gdf.to_json())
    return geojson

def shapefile_to_geojson(shp_file):
    with tempfile.TemporaryDirectory() as tmpdir:
        with ZipFile(shp_file) as zip_file:
            zip_file.extractall(tmpdir)
        gdf = gpd.read_file(tmpdir)
    geojson = json.loads(gdf.to_json())
    return geojson

def save_geojson_to_shapefile(all_drawings, filename):
    with tempfile.TemporaryDirectory() as tmpdir:
        # Define schema
        schema = {
            'geometry': 'Point',
            'properties': [('Name', 'str'), ('SampleID', 'int')]
        }

        # Open a Fiona object
        shapefile_filepath = os.path.join(tmpdir, f"{filename}.shp")
        with fiona.open(shapefile_filepath, mode='w', driver='ESRI Shapefile', schema=schema, crs="EPSG:4326") as shp_file:
            for idx, feature in enumerate(all_drawings):
                if feature['geometry']['type'] == 'Point':
                    point = Point(feature['geometry']['coordinates'])
                    shape = {
                        'geometry': mapping(point),
                        'properties': {'Name': f"Sample {idx}", 'SampleID': idx + 1}
                    }
                    shp_file.write(shape)

        # Create a zip file containing the shapefile components
        with BytesIO() as buffer:
            with ZipFile(buffer, "w") as zip_file:
                for extension in ["shp", "shx", "dbf", "prj"]:
                    zip_file.write(os.path.join(tmpdir, f"{filename}.{extension}"), f"SamplePoints.{extension}")
            buffer.seek(0)
            return buffer.read()

st.title("📍 Create Sampling Points")

# Create an expander for the instructions
instructions_expander = st.expander("Click for instructions", expanded=False)
with instructions_expander:
    st.markdown("""
    **Objective:** Drop sample points within your field.

    💡 **Tip:** If you have saved a **boundary** on the **✏️ Draw a Field** page, it will be displayed on the map for easier reference. The map will be centered and zoomed to the field's location.

    1. **Find your field** on the map.
    2. **Drop points** using the **Point** tool on the map.
    3. When finished, click **Save to Shapefile** and download your resulting .zip containing your points.

    """, unsafe_allow_html=True)

    #File Uploader
    uploaded_file = st.file_uploader("Upload your zipped shapefile to set the frame to your boundary!", type=["zip"])
    load_boundary_button = st.button("Load boundary to map")

    if load_boundary_button:
        if uploaded_file is not None:
            file_content_type = uploaded_file.type
            if file_content_type == "application/json":
                st.session_state.uploaded_boundary = json.load(uploaded_file)
            elif file_content_type == "application/vnd.google-earth.kml+xml":
                st.session_state.uploaded_boundary = kml_to_geojson(uploaded_file)
            elif file_content_type == "application/zip":
                st.session_state.uploaded_boundary = shapefile_to_geojson(uploaded_file)
            else:
                st.error("Unsupported file format. Please upload a GeoJSON, KML, or Shapefile.")
                
            st.session_state.boundary_updated = True

# Create a horizontal layout for the buttons
button_col1, button_col2 = st.columns(2)
with button_col1:
    save_to_shapefile_button = st.button("Save points to Shapefile")
with button_col2:
    remove_field_button = st.button("Remove field")

# Calculate the bounding box of the saved polygons
def get_polygon_bounds(polygon_features):
    polygons = [shapely_shape(feature['geometry']) for feature in polygon_features if feature['geometry']['type'] == 'Polygon']
    if not polygons:
        return None

    multipolygon = MultiPolygon(polygons)
    return multipolygon.bounds

def get_uploaded_boundary_bounds(uploaded_boundary):
    if not uploaded_boundary:
        return None

    features = uploaded_boundary["features"]
    polygons = [shapely_shape(feature['geometry']) for feature in features if feature['geometry']['type'] in ['Polygon', 'MultiPolygon']]
    if not polygons:
        return None

    multipolygon = MultiPolygon(polygons)
    return multipolygon.bounds

# Set the map's initial location and zoom level based on the saved polygons or uploaded boundary
if 'saved_geography' in st.session_state:
    bounds = get_polygon_bounds(st.session_state.saved_geography)
elif st.session_state.uploaded_boundary:
    bounds = get_uploaded_boundary_bounds(st.session_state.uploaded_boundary)
else:
    bounds = None

if bounds:
    min_lon, min_lat, max_lon, max_lat = bounds
    center_lat = (min_lat + max_lat) / 2
    center_lon = (min_lon + max_lon) / 2
    location = [center_lat, center_lon]
    zoom_start = 15
else:
    location = [36.1256, -97.0665]
    zoom_start = 10

m = folium.Map(
    location=location,
    zoom_start=zoom_start,
    tiles="https://mt1.google.com/vt/lyrs=y@18&x={x}&y={y}&z={z}",
    attr="Google"
)

# Customize the options for the Draw plugin
draw_options = {
    "position": "topleft",
    "polyline": False,
    "circle": False,
    "rectangle": False,
    "polygon": False,
    "circlemarker": False,
    "marker": True,
}

draw_control = Draw(export=False, draw_options=draw_options)
draw_control.add_to(m)

# Check if there is a polygon saved in the session state
if 'saved_geography' in st.session_state:
    # Add the saved polygons to the map
    for feature in st.session_state.saved_geography:
        if feature['geometry']['type'] == 'Polygon':
            polygon = folium.GeoJson(
                data=feature,
                style_function=lambda x: {"fillColor": "blue", "color": "blue", "weight": 2},
            )
            polygon.add_to(m)

# Check if there is a polygons uploaded
if uploaded_file is not None:
    file_content_type = uploaded_file.type
    if file_content_type == "application/json":
        st.session_state.uploaded_boundary = json.load(uploaded_file)
    elif file_content_type == "application/vnd.google-earth.kml+xml":
        st.session_state.uploaded_boundary = kml_to_geojson(uploaded_file)
    elif file_content_type == "application/zip":
        st.session_state.uploaded_boundary = shapefile_to_geojson(uploaded_file)
    else:
        st.error("Unsupported file format. Please upload a GeoJSON, KML, or Shapefile.")
    
    st.session_state.boundary_updated = True

if st.session_state.uploaded_boundary and st.session_state.boundary_updated:
    for feature in st.session_state.uploaded_boundary["features"]:
        if feature["geometry"]["type"] == "Polygon" or feature["geometry"]["type"] == "MultiPolygon":
            polygon = folium.GeoJson(
                data=feature,
                style_function=lambda x: {"fillColor": "blue", "color": "blue", "weight": 2},
            )
            polygon.add_to(m)
    st.session_state.boundary_updated = False

# Display the map without columns
returned_objects = st_folium(m, width='100%', height=700, returned_objects=["all_drawings"])


# Define the placeholder for the download button
buttons_placeholder1 = st.empty()

if save_to_shapefile_button:
    if returned_objects and isinstance(returned_objects, dict) and 'all_drawings' in returned_objects and len(returned_objects['all_drawings']) > 0:
        shapefile_data = save_geojson_to_shapefile(returned_objects['all_drawings'], "SamplePoints")
        buttons_placeholder1.download_button("Download Shapefile", shapefile_data, "GeoMaker_Point_Shapefile.zip", "application/zip")
    else:
        st.warning("No markers found. Please add markers to the map.")


if remove_field_button:
    if 'saved_geography' in st.session_state:
        del st.session_state.saved_geography
        st.experimental_rerun()

# Disable the 'Remove field' button if there is no field on the map
if not ('saved_geography' in st.session_state and st.session_state.saved_geography):
    remove_field_button = False
    buttons_placeholder2.button("Remove field", disabled=True, key="remove_field_button_disabled")

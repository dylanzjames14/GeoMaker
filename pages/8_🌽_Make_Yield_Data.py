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
from lxml import etree
import pandas as pd
from shapely.geometry import Polygon
from shapely.affinity import translate
from shapely.ops import cascaded_union


# Functions 
def get_uploaded_boundary_gdf(uploaded_boundary):
    if not uploaded_boundary:
        return None
    gdf = gpd.GeoDataFrame.from_features(uploaded_boundary["features"], crs="EPSG:4326")
    return gdf

def get_centroid(polygon):
    return polygon.centroid

def get_offset(point1, point2):
    return point2.x - point1.x, point2.y - point1.y

def apply_offset(geometry, offset):
    return translate(geometry, xoff=offset[0], yoff=offset[1], zoff=0.0)

def make_yield(yield_shapefile_path, field_polygon, reference_centroid):
    if os.path.exists(yield_shapefile_path):
        gdf = read_shapefile_from_folder(yield_shapefile_path)
    else:
        st.error("Yield shapefile folder not found in the Data directory.")
        return

    # Calculate the centroid of the field polygon
    field_centroid = get_centroid(field_polygon)

    # Calculate the offset needed to align the centroids
    offset = get_offset(reference_centroid, field_centroid)

    # Display field centroid, yield centroid, and offset values
    st.write(f"Field Centroid: {field_centroid.x}, {field_centroid.y}")
    st.write(f"Yield Centroid: {reference_centroid.x}, {reference_centroid.y}")
    st.write(f"Offset (x, y): {offset}")

    # Apply the same offset to all observations in the original shapefile
    gdf["geometry"] = gdf["geometry"].apply(lambda x: apply_offset(x, offset))

    # Save the new shapefile in a temporary directory
    with tempfile.TemporaryDirectory() as tmpdir:
        gdf.to_file(os.path.join(tmpdir, "new_yield.shp"))

        # Create a zip file containing the shapefile components
        with BytesIO() as buffer:
            with ZipFile(buffer, "w") as zip_file:
                for extension in ["shp", "shx", "dbf", "prj"]:
                    zip_file.write(os.path.join(tmpdir, f"new_yield.{extension}"), f"new_yield.{extension}")
            buffer.seek(0)
            return buffer.read()

def read_shapefile_from_folder(folder_path):
    # Find the .shp file in the folder (case-insensitive)
    shapefile_path = next((file for file in os.listdir(folder_path) if file.lower().endswith(".shp")), None)
    if shapefile_path:
        gdf = gpd.read_file(os.path.join(folder_path, shapefile_path))
    else:
        raise FileNotFoundError("No .shp file found in the shapefile folder.")
    return gdf

if 'uploaded_boundary' not in st.session_state:
    st.session_state.uploaded_boundary = None

if 'boundary_updated' not in st.session_state:
    st.session_state.boundary_updated = False

st.set_page_config(layout="wide")

def kml_to_geojson(kml_file):
    with kml_file as f:
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
            'properties': [('Name', 'str'), ('YieldID', 'int')]
        }

        # Open a Fiona object
        shapefile_filepath = os.path.join(tmpdir, f"{filename}.shp")
        with fiona.open(shapefile_filepath, mode='w', driver='ESRI Shapefile', schema=schema, crs="EPSG:4326") as shp_file:
            for idx, feature in enumerate(all_drawings):
                if feature['geometry']['type'] == 'Point':
                    point = Point(feature['geometry']['coordinates'])
                    shape = {
                        'geometry': mapping(point),
                        'properties': {'Name': f"Yield {idx}", 'YieldID': idx + 1}
                    }
                    shp_file.write(shape)

        # Create a zip file containing the shapefile components
        with BytesIO() as buffer:
            with ZipFile(buffer, "w") as zip_file:
                for extension in ["shp", "shx", "dbf", "prj"]:
                    zip_file.write(os.path.join(tmpdir, f"{filename}.{extension}"), f"YieldPoints.{extension}")
            buffer.seek(0)
            return buffer.read()

st.title("🌽 Create Yield Data")
st.warning("This application is currently under development. Stay tuned!")

# Create an expander for the instructions
instructions_expander = st.expander("Click for instructions", expanded=False)
with instructions_expander:
    st.markdown("""
    **Objective:** Create yield data for your field.

    💡 **Tip:** If you have saved a **boundary** on the **✏️ Draw a Field** page, it will be displayed on the map for easier reference. The map will be centered and zoomed to the field's location.

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
    "marker": False,
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
                style_function=lambda x: {"fillColor": "blue", "color": "blue", "weight": 1, "fillOpacity": 0.3}
            )
            polygon.add_to(m)

if st.session_state.uploaded_boundary:
    uploaded_boundary = folium.GeoJson(
        data=st.session_state.uploaded_boundary,
        style_function=lambda x: {"fillColor": "green", "color": "green", "weight": 1, "fillOpacity": 0.3}
    )
    uploaded_boundary.add_to(m)

#Display the map
st_folium(m, width='100%', height=800)

# Add the 'Make Yield' button at the end of the script
uploaded_boundary_gdf = get_uploaded_boundary_gdf(st.session_state.uploaded_boundary)
if uploaded_boundary_gdf is not None:
    field_multipolygon = cascaded_union(uploaded_boundary_gdf.geometry)
    field_centroid = field_multipolygon.representative_point()

    reference_centroid = Point(147.30171288325138, -34.887623172819644)

    if st.button("Make Yield"):
        yield_shapefile_path = "Data/Yield"
        new_yield_zip = make_yield(yield_shapefile_path, uploaded_boundary_gdf.unary_union, reference_centroid)
        if new_yield_zip:
            st.download_button("Download Shapefile", new_yield_zip, "Yield_Shapefile.zip")
            st.success("Congratulations, your new yield file has been made successfully!")

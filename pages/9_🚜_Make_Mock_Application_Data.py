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
from collections import OrderedDict
from dateutil.parser import parse as parse_date

st.set_page_config(page_title="Geomaker", page_icon="🌍", layout="wide")

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

def make_application(application_shapefile_path, field_polygon, reference_centroid, Product, rate_adjustment, selected_date):
    if os.path.exists(application_shapefile_path):
        gdf = read_shapefile_from_folder(application_shapefile_path)
    else:
        st.error("Data not found in the Data directory.")
        return

    # Update the 'Product' column value
    gdf['Product'] = product_name


    # Apply rate adjustment to 'AppliedRate' column
    gdf['AppliedRate'] = gdf['AppliedRate'] * rate_adjustment

    # If a date has been selected, update the 'Time' and 'IsoTime' columns
    if selected_date:
        for column in ["Time", "IsoTime"]:
            if column in gdf.columns:
                gdf[column] = gdf[column].apply(lambda x: update_date(x, selected_date))

    # Calculate the centroid of the field polygon
    field_centroid = get_centroid(field_polygon)

    # Calculate the offset needed to align the centroids
    offset = get_offset(reference_centroid, field_centroid)

    # Apply the same offset to all observations in the original shapefile
    gdf["geometry"] = gdf["geometry"].apply(lambda x: apply_offset(x, offset))

    # Save the new shapefile in a temporary directory
    with tempfile.TemporaryDirectory() as tmpdir:
        gdf.to_file(os.path.join(tmpdir, "Application.shp"))

        # Create a zip file containing the shapefile components
        with BytesIO() as buffer:
            with ZipFile(buffer, "w") as zip_file:
                for extension in ["shp", "shx", "dbf", "prj"]:
                    zip_file.write(os.path.join(tmpdir, f"Application.{extension}"), f"Application.{extension}")
            buffer.seek(0)
            return buffer.read()

def update_date(old_date_str, new_date):
    # Parse the old date
    old_date = parse_date(old_date_str)

    # Replace the year, month, and day with the selected date's
    new_date = old_date.replace(year=new_date.year, month=new_date.month, day=new_date.day)

    # Format the new date according to the format of the old date
    if "T" in old_date_str:  # IsoTime
        return new_date.isoformat()[:-3] + "Z"
    else:  # Time
        return new_date.strftime("%m/%d/%Y %I:%M:%S %p")

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

if 'new_application_zip' not in st.session_state:
    st.session_state.new_application_zip = None

def shapefile_to_geojson(shp_file):
    with tempfile.TemporaryDirectory() as tmpdir:
        with ZipFile(shp_file) as zip_file:
            zip_file.extractall(tmpdir)
        gdf = gpd.read_file(tmpdir)
    geojson = json.loads(gdf.to_json())
    return geojson

def save_geojson_to_shapefile(all_drawings, filename, crop):
    with tempfile.TemporaryDirectory() as tmpdir:
        # Define schema
        schema = {
            'geometry': 'Polygon',
            'properties': [('Name', 'str'), ('Crop', 'str')]
        }

        # Open a Fiona object
        shapefile_filepath = os.path.join(tmpdir, f"{filename}.shp")
        with fiona.open(shapefile_filepath, mode='w', driver='ESRI Shapefile', schema=schema, crs="EPSG:4326") as shp_file:
            for idx, feature in enumerate(all_drawings):
                if feature['geometry']['type'] == 'Polygon':
                    polygon = shapely_shape(feature['geometry'])
                    shape = {
                        'geometry': mapping(polygon),
                        'properties': {'Name': f"Polygon {idx}", 'Crop': crop}
                    }
                    shp_file.write(shape)

        # Create a zip file containing the shapefile components
        with BytesIO() as buffer:
            with ZipFile(buffer, "w") as zip_file:
                for extension in ["shp", "shx", "dbf", "prj"]:
                    zip_file.write(os.path.join(tmpdir, f"{filename}.{extension}"), f"{filename}.{extension}")
            buffer.seek(0)
            return buffer.read()

st.title("🚜 Make Mock Application Data")
st.warning("⚠️ This page is currently a work in progress. Rates are defaulted to a liquid fertilizer rate averaging ~17 gal/ac. Please notify Dylan of any issues you experience.")

# Create an expander for the instructions
instructions_expander = st.expander("Click for instructions", expanded=False)
with instructions_expander:
    st.markdown("""
    This application enables you to generate application data for your field by following these steps:

    1. **Add a field boundary**: If you have already saved a drawn boundary on the **✏️ Draw a Field** page, it will be automatically displayed on the map. You may also upload a zipped boundary using the file uploader below. 

    2. **Generate application data**: Once you have a boundary, click the "Make Data" button to generate the application data for your field. The application will create a new shapefile containing the application data, which you can download by clicking the "Download Shapefile" button.

    💡 **Tip:** If you need to add or modify your field boundary, visit the **✏️ Draw a Field** page and follow the instructions there.
    """, unsafe_allow_html=True)

    #File Uploader
    uploaded_file = st.file_uploader("Upload your zipped boundary file (shp,kml,geojson) to set the frame to your boundary!", type=["zip"])
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

# Display the map in the first column
col1, col2 = st.columns(2)

with col1:
    st_folium(m, width='100%', height=750)

# Add the 'Make Data' button
with col2:
    # Define application dates
    selected_date = st.date_input("Application date:", value=None)
    if selected_date:
        st.session_state.selected_date = selected_date
    # Get the user's selected product
    product_name = st.text_input("Enter a product:", value="")


    # Get the default value for the selected crop
    default_value = (0)

    # Display the slider for rate adjustment
    rate_adjustment_input = st.slider(
        "Rate adjustment (%)",
        min_value=-200,
        max_value=850,
        value=default_value,
        step=1,
    )
    rate_adjustment = (rate_adjustment_input + 100) / 100
    
    #You have no boundary warn
    if ('uploaded_boundary' not in st.session_state or st.session_state.uploaded_boundary is None) and \
    ('saved_geography' not in st.session_state or not any(feature['geometry']['type'] in ['Polygon', 'MultiPolygon'] for feature in st.session_state.saved_geography)):
        st.warning("Please add a boundary to continue. Read instructions for more information.")
        

    if ('uploaded_boundary' in st.session_state and st.session_state.uploaded_boundary is not None) or \
    ('saved_geography' in st.session_state and any(feature['geometry']['type'] in ['Polygon', 'MultiPolygon'] for feature in st.session_state.saved_geography)):
        uploaded_boundary_gdf = get_uploaded_boundary_gdf(st.session_state.uploaded_boundary)
        if uploaded_boundary_gdf is not None:
            field_multipolygon = cascaded_union(uploaded_boundary_gdf.geometry)
            field_centroid = field_multipolygon.representative_point()

        else:
            field_multipolygon = cascaded_union([shapely_shape(feature['geometry']) for feature in st.session_state.saved_geography if feature['geometry']['type'] in ['Polygon', 'MultiPolygon']])
            field_centroid = field_multipolygon.representative_point()

        reference_centroid = Point(-97.85271468657078, 39.83161673804731)

        if st.button("Make Data"):
            if product_name:
                with st.spinner("Creating your application file. Please be patient, this will take a couple minutes."):
                    application_shapefile_path = "Data/Application"
                    # call make_application function with all the arguments
                    new_application_zip = make_application(application_shapefile_path, field_multipolygon, reference_centroid, product_name, rate_adjustment, st.session_state.selected_date)

                if new_application_zip:
                    st.download_button("Download Shapefile", new_application_zip, "Application_Shapefile.zip")
                    st.success("Congratulations, your new application file has been made successfully!")
            else:
                st.warning("Please input your product before proceeding.")

    if st.session_state.new_application_zip:
        st.download_button("Download Shapefile", st.session_state.new_application_zip, "Application_Shapefile.zip")

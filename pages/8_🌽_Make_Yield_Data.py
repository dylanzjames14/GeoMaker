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

st.set_page_config(layout="wide")

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

save_button = st.button("Save to Shapefile")
if save_button:
    # Get the drawings from the Draw control
    all_drawings = draw_control.data

    if not all_drawings:
        st.warning("No points were drawn on the map.")
    else:
        # Save the drawings to a shapefile
        shapefile_data = save_geojson_to_shapefile(all_drawings, "YieldPoints")
        st.download_button(
            label="Download Shapefile",
            data=shapefile_data,
            file_name="YieldPoints.zip",
            mime="application/zip"
        )


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

st.set_page_config(layout="wide")

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
instructions_expander = st.expander("Instructions", expanded=False)
with instructions_expander:
    st.markdown("""
    - Find your field using the map and drop points using the **Point** tool on the map.
    - If you have saved a field boundary on the '✏️ Draw a field' page, it will be displayed on the map. The map will be centered and zoomed to the field's location.
    - Once complete, click **Save to Shapefile** and download your resulting .zip containing your points.
    """)

# Create an empty placeholder for the buttons
buttons_placeholder = st.empty()

# Calculate the bounding box of the saved polygons
def get_polygon_bounds(polygon_features):
    polygons = [shapely_shape(feature['geometry']) for feature in polygon_features if feature['geometry']['type'] == 'Polygon']
    if not polygons:
        return None

    multipolygon = MultiPolygon(polygons)
    return multipolygon.bounds

# Set the map's initial location and zoom level based on the saved polygons
if 'saved_geography' in st.session_state:
    bounds = get_polygon_bounds(st.session_state.saved_geography)
    if bounds:
        min_lon, min_lat, max_lon, max_lat = bounds
        center_lat = (min_lat + max_lat) / 2
        center_lon = (min_lon + max_lon) / 2
        location = [center_lat, center_lon]
        zoom_start = 15
    else:
        location = [36.1256, -97.0665]
        zoom_start = 10
else:
    location = [36.1256, -97.0665]
    zoom_start = 10

m = folium.Map(
    location=location,
    zoom_start=zoom_start,
    tiles="https://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}",
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
else:
    st.warning("No saved polygons found. Please draw and save a polygon on the other page.")

# Display the map without columns
returned_objects = st_folium(m, width=1000, height=550, returned_objects=["all_drawings"])

# Show the buttons above the map
if buttons_placeholder.button("Save to Shapefile"):
    if returned_objects and isinstance(returned_objects, dict) and 'all_drawings' in returned_objects and len(returned_objects['all_drawings']) > 0:
        shapefile_data = save_geojson_to_shapefile(returned_objects['all_drawings'], "SamplePoints")
        buttons_placeholder.download_button("Download Shapefile", shapefile_data, "GeoMaker_Point_Shapefile.zip", "application/zip")
    else:
        st.warning("No markers found. Please add markers to the map.")

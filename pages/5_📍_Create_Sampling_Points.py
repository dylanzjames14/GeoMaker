import streamlit as st
import folium
from streamlit_folium import st_folium
from folium.plugins import Draw
from shapely.geometry import Point, mapping, shape as shapely_shape, MultiPolygon
import json
import tempfile
from io import BytesIO
import fiona
import os

# Initialize session state variables
if 'saved_geography' not in st.session_state:
    st.session_state.saved_geography = []

st.set_page_config(page_title="Geomaker", page_icon="🌍", layout="wide")

# Function to save drawn points to a shapefile
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
                        'properties': {'Name': f"Sample {idx + 1}", 'SampleID': idx + 1}
                    }
                    shp_file.write(shape)

        # Create a zip file containing the shapefile components
        with BytesIO() as buffer:
            with ZipFile(buffer, "w") as zip_file:
                for extension in ["shp", "shx", "dbf", "prj"]:
                    zip_file.write(os.path.join(tmpdir, f"{filename}.{extension}"), f"{filename}.{extension}")
            buffer.seek(0)
            return buffer.read()

# Function to get bounds of saved polygons
def get_polygon_bounds(polygon_features):
    polygons = [shapely_shape(feature['geometry']) for feature in polygon_features if feature['geometry']['type'] in ['Polygon', 'MultiPolygon']]
    if not polygons:
        return None
    multipolygon = MultiPolygon(polygons)
    return multipolygon.bounds

# Application title
st.title("📍 Create Sampling Points")

# Instructions expander
with st.expander("Click for instructions", expanded=False):
    st.markdown("""
    **Objective:** Drop sample points within your field.

    💡 **Tip:** If you have saved a **boundary** on the **✏️ Draw a Field** page, it will be displayed on the map for easier reference. The map will be centered and zoomed to the field's location.

    1. **Find your field** on the map.
    2. **Drop points** using the **Point** tool on the map.
    3. When finished, click **Save points to Shapefile** and download your resulting `.zip` containing your points.
    """)

# Buttons for actions
button_col1, button_col2 = st.columns(2)
with button_col1:
    save_to_shapefile_button = st.button("Save points to Shapefile")
with button_col2:
    if st.session_state.saved_geography:
        remove_field_button = st.button("Remove field")
    else:
        st.button("Remove field", disabled=True)

# Determine map center and zoom
if st.session_state.saved_geography:
    bounds = get_polygon_bounds(st.session_state.saved_geography)
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

# Initialize map
m = folium.Map(
    location=location,
    zoom_start=zoom_start,
    tiles="https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}",
    attr="Google"
)

# Add drawing control
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

# Add saved boundary to map
if st.session_state.saved_geography:
    for feature in st.session_state.saved_geography:
        folium.GeoJson(
            data=feature,
            style_function=lambda x: {"fillColor": "blue", "color": "blue", "weight": 2, "fillOpacity": 0.3},
        ).add_to(m)

# Display the map
returned_objects = st_folium(m, width='100%', height=600, returned_objects=["all_drawings"])

# Handle save to shapefile action
if save_to_shapefile_button:
    if returned_objects and 'all_drawings' in returned_objects and returned_objects['all_drawings']:
        shapefile_data = save_geojson_to_shapefile(returned_objects['all_drawings'], "SamplePoints")
        st.download_button("Download Shapefile", shapefile_data, "SamplePoints.zip", "application/zip")
    else:
        st.warning("No markers found. Please add markers to the map before saving.")

# Handle remove field action
if 'remove_field_button' in locals() and remove_field_button:
    st.session_state.saved_geography = []
    st.experimental_rerun()

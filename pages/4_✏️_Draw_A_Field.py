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
from shapely.geometry import shape as shapely_shape, mapping
import simplekml
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut

st.set_page_config(page_title="Geomaker", page_icon="🌍", layout="wide")

def get_polygon_bounds(features):
    min_lat, min_lon, max_lat, max_lon = None, None, None, None
    for feature in features:
        if feature['geometry']['type'] == 'Polygon':
            polygon = shapely_shape(feature['geometry'])
            if min_lat is None or polygon.bounds[1] < min_lat:
                min_lat = polygon.bounds[1]
            if min_lon is None or polygon.bounds[0] < min_lon:
                min_lon = polygon.bounds[0]
            if max_lat is None or polygon.bounds[3] > max_lat:
                max_lat = polygon.bounds[3]
            if max_lon is None or polygon.bounds[2] > max_lon:
                max_lon = polygon.bounds[2]
    return min_lon, min_lat, max_lon, max_lat

def save_geojson_to_kml(all_drawings, filename):
    kml = simplekml.Kml()

    for idx, feature in enumerate(all_drawings):
        if feature['geometry']['type'] == 'Polygon':
            polygon = shapely_shape(feature['geometry'])
            kml.newpolygon(name=f"Polygon {idx}", outerboundaryis=list(polygon.exterior.coords))

    kml_str = kml.kml()
    return kml_str


def save_geojson_to_shapefile(all_drawings, filename):
    with tempfile.TemporaryDirectory() as tmpdir:
        # Define schema
        schema = {
            'geometry': 'Polygon',
            'properties': [('Name', 'str')]
        }

        # Open a Fiona object
        shapefile_filepath = os.path.join(tmpdir, f"{filename}.shp")
        with fiona.open(shapefile_filepath, mode='w', driver='ESRI Shapefile', schema=schema, crs="EPSG:4326") as shp_file:
            for idx, feature in enumerate(all_drawings):
                if feature['geometry']['type'] == 'Polygon':
                    polygon = shapely_shape(feature['geometry'])
                    shape = {
                        'geometry': mapping(polygon),
                        'properties': {'Name': f"Polygon {idx}"}
                    }
                    shp_file.write(shape)

        # Create a zip file containing the shapefile components
        with BytesIO() as buffer:
            with ZipFile(buffer, "w") as zip_file:
                for extension in ["shp", "shx", "dbf", "prj"]:
                    zip_file.write(os.path.join(tmpdir, f"{filename}.{extension}"), f"{filename}.{extension}")
            buffer.seek(0)
            return buffer.read()


st.title("✏️ Draw a Field")

# Create an expander for the instructions
instructions_expander = st.expander("Click for instructions", expanded=False)
with instructions_expander:
    st.markdown("""
    **Objective:** Draw a field boundary and save its boundary file.

    1. **Navigate** to your field on the map.
    2. **Draw a field boundary** using the map tools.
    3. When finished, click the appropriate button to **save your drawn field boundary**.

    💡 **Tip:** If you click '**Save Field**', you can utilize the field boundary in the **📍 Create Sampling Points** application.
    """, unsafe_allow_html=True)

zoom_start = 11

geolocator = Nominatim(user_agent="myGeocoder")
search_location = st.text_input("Search for a location:")

# Initialize location to default or based on 'saved_geography' in session state
location = [36.1256, -97.0665]
if 'saved_geography' in st.session_state:
    bounds = get_polygon_bounds(st.session_state.saved_geography)
    if bounds:
        min_lon, min_lat, max_lon, max_lat = bounds
        center_lat = (min_lat + max_lat) / 2
        center_lon = (min_lon + max_lon) / 2
        location = [center_lat, center_lon]
        zoom_start = 15

# Override location and zoom if a search location was provided
if search_location:
    try:
        geo_location = geolocator.geocode(search_location)
        if geo_location:
            st.write(f"Latitude: {geo_location.latitude}, Longitude: {geo_location.longitude}")
            location = [geo_location.latitude, geo_location.longitude]
            zoom_start = 15
        else:
            st.warning("Location not found. Please try another search query.")
    except GeocoderTimedOut:
        st.warning("Geocoding service timed out. Please try again.")

# Initialize the map
m = folium.Map(
    location=location,
    zoom_start=zoom_start,
    tiles="https://mt1.google.com/vt/lyrs=y@18&x={x}&y={y}&z={z}",
    attr="Google"
)

draw_options = {
    "position": "topleft",
    "polyline": False,
    "circle": False,
    "rectangle": True,
    "polygon": True,
    "circlemarker": False,
    "marker": False,
}

draw_control = Draw(export=False, draw_options=draw_options)
draw_control.add_to(m)

# Add the saved polygons to the map
if 'saved_geography' in st.session_state:
    for feature in st.session_state.saved_geography:
        if feature['geometry']['type'] == 'Polygon':
            polygon = folium.GeoJson(
                data=feature,
                style_function=lambda x: {"fillColor": "blue", "color": "blue", "weight": 1, "fillOpacity": 0.3}
            )
            polygon.add_to(m)

# Create two columns
col1, col2 = st.columns([3, 1])

# Place the map in the first column
with col1:
    returned_objects = st_folium(m, width='100%', height=650, returned_objects=["all_drawings"])

# Place the buttons in the second column
with col2:
    save_shapefile_button = st.button("Save to Shapefile")
    save_kml_button = st.button("Save KML")
    save_geojson_button = st.button("Save GEOJSON")
    save_for_sampling_button = st.button("Save Field")
    remove_field_button = st.button("Remove field", key="remove_field_button")

# 'Remove field' button action moved outside
if remove_field_button:
    if 'saved_geography' in st.session_state:
        del st.session_state.saved_geography
        st.experimental_rerun()

if save_shapefile_button or save_kml_button or save_geojson_button or save_for_sampling_button:
    all_drawings = []
    if isinstance(returned_objects, dict) and 'all_drawings' in returned_objects and returned_objects['all_drawings']:
        all_drawings = returned_objects['all_drawings']
    if 'saved_geography' in st.session_state:
        all_drawings.extend(st.session_state.saved_geography)

    if len(all_drawings) > 0:
        if save_shapefile_button:
            shapefile_data = save_geojson_to_shapefile(all_drawings, "DrawnPolygons")
            col1.download_button("Download Shapefile", shapefile_data, "Drawn_Polygons_Shapefile.zip", "application/zip")

        if save_kml_button:
            kml_data = save_geojson_to_kml(all_drawings, "DrawnPolygons")
            col1.download_button("Download KML", kml_data, "Drawn_Polygons.kml", "application/vnd.google-earth.kml+xml")

        if save_geojson_button:
            geojson_data = json.dumps({"type": "FeatureCollection", "features": all_drawings})
            col1.download_button("Download GEOJSON", geojson_data, "Drawn_Polygons.geojson", "application/geo+json")

        if save_for_sampling_button:
            st.session_state.saved_geography = all_drawings
            st.success("Geography saved for use on the other pages!")
    else:
        st.warning("No polygons found. Please draw polygons on the map.")

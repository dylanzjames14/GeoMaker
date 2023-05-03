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

st.set_page_config(layout="wide")

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

def save_geojson_to_kml(all_drawings, filename):
    kml = simplekml.Kml()
    for idx, feature in enumerate(all_drawings):
        if feature['geometry']['type'] == 'Polygon':
            polygon = shapely_shape(feature['geometry'])
            kml.newpolygon(name=f"Polygon {idx}", outerboundaryis=list(polygon.exterior.coords))
    return kml.kml()

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

# Add a geocoder instance
geolocator = Nominatim(user_agent="myGeocoder")

# Add a search box to your app
search_location = st.text_input("Search for a location:")

m = folium.Map(
    location=[36.1256, -97.0665],
    zoom_start=10,
    tiles="https://mt1.google.com/vt/lyrs=y@18&x={x}&y={y}&z={z}",
    attr="Google"
)

if search_location:
    try:
        location = geolocator.geocode(search_location)
        if location:
            st.write(f"Latitude: {location.latitude}, Longitude: {location.longitude}")
            m = folium.Map(
                location=[location.latitude, location.longitude],
                zoom_start=15,
                tiles="https://mt1.google.com/vt/lyrs=y@18&x={x}&y={y}&z={z}",
                attr="Google"
            )
        else:
            st.warning("Location not found. Please try another search query.")
    except GeocoderTimedOut:
        st.warning("Geocoding service timed out. Please try again.")

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

# Display the map without columns
returned_objects = st_folium(m, width='100%', height=800, returned_objects=["all_drawings"])

# Create an empty placeholder for the buttons
buttons_placeholder = st.empty()

# Save buttons in columns
col1, col2, col3, col4 = st.columns(4)
save_shapefile_button = col1.button("Save to Shapefile")
save_kml_button = col2.button("Save KML")
save_geojson_button = col3.button("Save GEOJSON")
save_for_sampling_button = col4.button("Save Field")

if save_shapefile_button:
    if isinstance(returned_objects, dict) and 'all_drawings' in returned_objects and len(returned_objects['all_drawings']) > 0:
        shapefile_data = save_geojson_to_shapefile(returned_objects['all_drawings'], "DrawnPolygons")
        col1.download_button("Download Shapefile", shapefile_data, "Drawn_Polygons_Shapefile.zip", "application/zip")
    else:
        col1.warning("No polygons found. Please draw polygons on the map.")

if save_kml_button:
    if isinstance(returned_objects, dict) and 'all_drawings' in returned_objects and len(returned_objects['all_drawings']) > 0:
        kml_data = save_geojson_to_kml(returned_objects['all_drawings'], "DrawnPolygons")
        col2.download_button("Download KML", kml_data, "Drawn_Polygons.kml", "application/vnd.google-earth.kml+xml")
    else:
        col2.warning("No polygons found. Please draw polygons on the map.")

if save_geojson_button:
    if isinstance(returned_objects, dict) and 'all_drawings' in returned_objects and len(returned_objects['all_drawings']) > 0:
        geojson_data = json.dumps({"type": "FeatureCollection", "features": returned_objects['all_drawings']})
        col3.download_button("Download GEOJSON", geojson_data, "Drawn_Polygons.geojson", "application/geo+json")
    else:
        col3.warning("No polygons found. Please draw polygons on the map.")

if save_for_sampling_button:
    if isinstance(returned_objects, dict) and 'all_drawings' in returned_objects and len(returned_objects['all_drawings']) > 0:
        st.session_state.saved_geography = returned_objects['all_drawings']
        st.success("Geography saved for sampling.")
    else:
        st.warning("No polygons found. Please draw polygons on the map.")

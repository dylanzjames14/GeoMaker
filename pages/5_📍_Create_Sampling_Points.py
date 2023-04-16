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
st.markdown("""
1. Find your field using the map and drop points using the **Point** tool on the map.
2. Once complete, click **Save to Shapefile** and download your resulting .zip containing your points.
""")

# Create an empty placeholder for the buttons
buttons_placeholder = st.empty()

m = folium.Map(
    location=[36.1256, -97.0665],
    zoom_start=10,
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

# Display the map without columns
returned_objects = st_folium(m, width=1000, height=550, returned_objects=["all_drawings"])

# Show the buttons above the map
if buttons_placeholder.button("Save to Shapefile"):
    if returned_objects and isinstance(returned_objects, dict) and 'all_drawings' in returned_objects and len(returned_objects['all_drawings']) > 0:
        shapefile_data = save_geojson_to_shapefile(returned_objects['all_drawings'], "SamplePoints")
        buttons_placeholder.download_button("Download Shapefile", shapefile_data, "GeoMaker_Point_Shapefile.zip", "application/zip")
    else:
        st.warning("No markers found. Please add markers to the map.")

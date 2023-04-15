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

st.title("📍 Draw Polygons")
st.markdown("""
1. Navigate to your field on the map.
2. Draw polygons using the 'Polygon', 'Rectangle', or 'Circle' tool on the map.
3. Once complete, click **Save to Shapefile** and download your resulting .zip containing your polygons.
""")

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
    "circle": True,
    "rectangle": True,
    "polygon": True,
    "circlemarker": False,
    "marker": False,
}

draw_control = Draw(export=False, draw_options=draw_options)
draw_control.add_to(m)

# Display the map without columns
returned_objects = st_folium(m, width=1000, height=600, returned_objects=["all_drawings"])

if st.button("Save to Shapefile"):
    if isinstance(returned_objects, dict) and 'all_drawings' in returned_objects and len(returned_objects['all_drawings']) > 0:
        shapefile_data = save_geojson_to_shapefile(returned_objects['all_drawings'], "DrawnPolygons")
        st.download_button("Download Shapefile", shapefile_data, "Drawn_Polygons_Shapefile.zip", "application/zip")
    else:
        st.warning("No polygons found. Please draw polygons on the map.")

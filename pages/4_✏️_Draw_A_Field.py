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
st.markdown("""
1. Navigate to your field on the map and draw a field boundary using the map tools.
2. Once complete, click the appropriate button to save your drawn polygons.
""")

# Save buttons in columns
col1, col2, col3 = st.columns(3)
save_shapefile_button = col1.button("Save to Shapefile")
save_kml_button = col2.button("Save KML")
save_geojson_button = col3.button("Save GEOJSON")

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
    "rectangle": True,
    "polygon": True,
    "circlemarker": False,
    "marker": False,
}

draw_control = Draw(export=False, draw_options=draw_options)
draw_control.add_to(m)

# Display the map without columns

returned_objects = st_folium(m, width=1000, height=550, returned_objects=["all_drawings"])

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

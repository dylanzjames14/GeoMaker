import streamlit as st
import folium
from streamlit_folium import st_folium
from folium.plugins import Draw
from shapely.geometry import shape, mapping, Polygon
from shapely.wkt import loads as load_wkt
import json
import tempfile
from zipfile import ZipFile
from io import BytesIO
import os
import fiona
import simplekml
import geopandas as gpd  # Ensure geopandas is installed

# Set page configuration
st.set_page_config(page_title="Geomaker", page_icon="🌍", layout="wide")

# Initialize session state
if 'saved_geography' not in st.session_state:
    st.session_state.saved_geography = []

# Function to calculate polygon bounds
def calculate_polygon_bounds(features):
    if not features:
        return None
    polygons = [shape(feature['geometry']) for feature in features if feature['geometry']['type'] in ['Polygon', 'MultiPolygon']]
    if not polygons:
        return None
    minx, miny, maxx, maxy = polygons[0].bounds
    for polygon in polygons[1:]:
        bounds = polygon.bounds
        minx = min(minx, bounds[0])
        miny = min(miny, bounds[1])
        maxx = max(maxx, bounds[2])
        maxy = max(maxy, bounds[3])
    return minx, miny, maxx, maxy

# Function to convert GeoJSON to Shapefile
def convert_geojson_to_shapefile(features, filename):
    with tempfile.TemporaryDirectory() as tmpdir:
        schema = {
            'geometry': 'Polygon',
            'properties': {'id': 'int'},
        }
        shapefile_path = os.path.join(tmpdir, f"{filename}.shp")
        with fiona.open(shapefile_path, 'w', driver='ESRI Shapefile', schema=schema, crs="EPSG:4326") as shp:
            for idx, feature in enumerate(features):
                geom = feature['geometry']
                shp.write({
                    'geometry': geom,
                    'properties': {'id': idx},
                })
        # Zip the shapefile components
        with BytesIO() as buffer:
            with ZipFile(buffer, 'w') as zip_file:
                for ext in ['.shp', '.shx', '.dbf', '.prj']:
                    file_path = os.path.join(tmpdir, f"{filename}{ext}")
                    if os.path.exists(file_path):
                        zip_file.write(file_path, arcname=f"{filename}{ext}")
            buffer.seek(0)
            return buffer.read()

# Function to convert GeoJSON to KML
def convert_geojson_to_kml(features, filename):
    kml = simplekml.Kml()
    for idx, feature in enumerate(features):
        geom = shape(feature['geometry'])
        if geom.geom_type == 'Polygon':
            kml.newpolygon(
                name=f"Polygon {idx}",
                outerboundaryis=list(geom.exterior.coords)
            )
        elif geom.geom_type == 'MultiPolygon':
            for poly in geom.geoms:
                kml.newpolygon(
                    name=f"Polygon {idx}",
                    outerboundaryis=list(poly.exterior.coords)
                )
    return kml.kml()

# Function to load shapefile from ZIP and convert to GeoJSON
def shapefile_zip_to_geojson(zip_file):
    with tempfile.TemporaryDirectory() as tmpdir:
        # Save the uploaded zip file to a temporary directory
        zip_path = os.path.join(tmpdir, "uploaded_shapefile.zip")
        with open(zip_path, "wb") as f:
            f.write(zip_file.getvalue())
        try:
            with ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(tmpdir)
            shp_files = [os.path.join(tmpdir, file) for file in os.listdir(tmpdir) if file.endswith('.shp')]
            if not shp_files:
                st.error("No .shp file found in the ZIP archive.")
                return None
            gdf = gpd.read_file(shp_files[0])
            geojson = json.loads(gdf.to_json())
            return geojson
        except Exception as e:
            st.error(f"Failed to read shapefile from ZIP: {e}")
            return None

# Application title
st.title("✏️ Draw a Field or Upload Boundary")

# Instructions expander
with st.expander("Click for instructions", expanded=False):
    st.markdown("""
    **Objective:** Draw a field boundary or upload a boundary file and save its boundary.

    1. **Draw a Field**:
        - Navigate to your field on the map.
        - Use the drawing tools to draw your field boundary.
        - Click "Save Boundary" to save your drawn boundary.

    2. **Upload Boundary**:
        - Expand the "Boundary Input" section below.
        - Upload your boundary file (Shapefile ZIP or WKT).
        - Click "Load to Map" to add the boundary to the map.
        - The boundary will automatically be saved.

    💡 **Tip:** Utilize the field boundary in various applications within this tool.
    """)

# Boundary Input Section within an Expander
with st.expander("Boundary Input"):
    st.markdown("**Upload a Shapefile ZIP file or paste WKT text:**")
    uploaded_file = st.file_uploader("Upload Shapefile ZIP file:", type=["zip"])
    st.markdown("**OR**")
    st.code("Example WKT Format: POLYGON ((-97.069 36.126, -97.067 36.126, -97.067 36.125, -97.069 36.125, -97.069 36.126))")
    wkt_input = st.text_area("Paste your WKT here:")
    submit_boundary = st.button("Load to Map")

    if submit_boundary:
        if uploaded_file is not None:
            # Handle Shapefile ZIP upload
            geojson_data = shapefile_zip_to_geojson(uploaded_file)
            if geojson_data:
                st.session_state.saved_geography = geojson_data['features']
                st.success("Shapefile boundary added to the map!")
            else:
                st.error("Failed to load shapefile.")
        elif wkt_input:
            # Handle WKT input
            try:
                polygon_shape = load_wkt(wkt_input)
                if not polygon_shape.is_valid or polygon_shape.is_empty:
                    st.error("Invalid WKT geometry.")
                else:
                    geojson_geometry = mapping(polygon_shape)
                    geojson_feature = {
                        "type": "Feature",
                        "geometry": geojson_geometry,
                        "properties": {}
                    }
                    # Add to saved geography
                    st.session_state.saved_geography = [geojson_feature]
                    st.success("WKT polygon added to the map!")
            except Exception as e:
                st.error(f"Error processing WKT: {e}")
        else:
            st.warning("Please upload a shapefile ZIP or enter WKT before clicking 'Load to Map'.")

# Action buttons above the map
button_container = st.container()

with button_container:
    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        save_boundary = st.button("Save Boundary", key='save_boundary_top')
    with col2:
        remove_boundary = st.button("Remove Boundary", key='remove_boundary')
    with col3:
        save_shp = st.button("Save SHP", key='save_shp')
        shp_placeholder = st.empty()
    with col4:
        save_kml = st.button("Save KML", key='save_kml')
        kml_placeholder = st.empty()
    with col5:
        save_geojson = st.button("Save GeoJSON", key='save_geojson')
        geojson_placeholder = st.empty()

# Update location based on saved geography
if st.session_state.saved_geography:
    bounds = calculate_polygon_bounds(st.session_state.saved_geography)
    if bounds:
        minx, miny, maxx, maxy = bounds
        center_latitude = (miny + maxy) / 2
        center_longitude = (minx + maxx) / 2
        default_location = [center_latitude, center_longitude]
        default_zoom = 15
    else:
        default_location = [36.1256, -97.0665]
        default_zoom = 14
else:
    default_location = [36.1256, -97.0665]
    default_zoom = 14

# Initialize and configure the map
m = folium.Map(
    location=default_location,
    zoom_start=default_zoom,
    tiles="https://mt1.google.com/vt/lyrs=y@18&x={x}&y={y}&z={z}",
    attr="Google"
)

# Add drawing control to the map
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

# Display saved polygons on the map
if st.session_state.saved_geography:
    for feature in st.session_state.saved_geography:
        if feature['geometry']['type'] in ['Polygon', 'MultiPolygon']:
            folium.GeoJson(
                data=feature,
                style_function=lambda x: {
                    "fillColor": "blue",
                    "color": "blue",
                    "weight": 1,
                    "fillOpacity": 0.3
                }
            ).add_to(m)

# Map display
returned_objects = st_folium(m, width='100%', height=650, returned_objects=["all_drawings"])

# Handle Save Boundary action
if save_boundary:
    if 'all_drawings' in returned_objects and returned_objects['all_drawings']:
        new_drawings = returned_objects['all_drawings']
        # Save the drawn features to session storage
        st.session_state.saved_geography = new_drawings
        st.success("Boundary saved and available for use throughout the application.")
    elif st.session_state.saved_geography:
        st.success("Boundary is already saved.")
    else:
        st.warning("Please draw a polygon on the map or upload a boundary before saving.")

# Handle Remove Boundary action
if remove_boundary:
    if st.session_state.saved_geography:
        st.session_state.saved_geography = []
        st.success("Boundary removed.")
        st.experimental_rerun()
    else:
        st.warning("No boundary to remove.")

# Handle Save SHP action
if save_shp:
    if st.session_state.saved_geography:
        all_drawn_features = st.session_state.saved_geography
        shapefile_content = convert_geojson_to_shapefile(all_drawn_features, "DrawnPolygons")
        with col3:
            shp_placeholder.download_button(
                label="Download Shapefile",
                data=shapefile_content,
                file_name="Drawn_Polygons_Shapefile.zip",
                mime="application/zip",
                key='download_shp_file'
            )
    else:
        with col3:
            shp_placeholder.info("Please save a boundary before downloading the shapefile.")

# Handle Save KML action
if save_kml:
    if st.session_state.saved_geography:
        all_drawn_features = st.session_state.saved_geography
        kml_content = convert_geojson_to_kml(all_drawn_features, "DrawnPolygons")
        with col4:
            kml_placeholder.download_button(
                label="Download KML",
                data=kml_content,
                file_name="Drawn_Polygons.kml",
                mime="application/vnd.google-earth.kml+xml",
                key='download_kml_file'
            )
    else:
        with col4:
            kml_placeholder.info("Please save a boundary before downloading the KML file.")

# Handle Save GeoJSON action
if save_geojson:
    if st.session_state.saved_geography:
        all_drawn_features = st.session_state.saved_geography
        geojson_content = json.dumps({
            "type": "FeatureCollection",
            "features": all_drawn_features
        })
        with col5:
            geojson_placeholder.download_button(
                label="Download GeoJSON",
                data=geojson_content,
                file_name="Drawn_Polygons.geojson",
                mime="application/geo+json",
                key='download_geojson_file'
            )
    else:
        with col5:
            geojson_placeholder.info("Please save a boundary before downloading the GeoJSON file.")

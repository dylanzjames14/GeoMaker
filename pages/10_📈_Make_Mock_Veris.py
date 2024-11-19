import streamlit as st
import folium
from streamlit_folium import st_folium
from shapely.geometry import Point, LineString, Polygon, MultiPolygon, shape as shapely_shape
from shapely.ops import unary_union
import geopandas as gpd
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json

st.set_page_config(page_title="Geomaker - Veris Data Generator", page_icon="📈", layout="wide")

# Initialize session state
if 'uploaded_boundary' not in st.session_state:
    st.session_state.uploaded_boundary = None

if 'saved_geography' not in st.session_state:
    st.session_state.saved_geography = None

if 'veris_data' not in st.session_state:
    st.session_state.veris_data = None

# Title
st.title("📈 Make Mock Veris Data")

# Disclaimer
st.warning("**Disclaimer:** This page is under development and hasn't been thoroughly tested. Please use caution and report any issues you encounter.")

# Instructions
with st.expander("Click for instructions", expanded=False):
    st.markdown("""
    **Objective:** Generate mock Veris `.dat` files for your field.

    **Steps:**
    1. **Ensure you have a field boundary**: Use the **✏️ Draw a Field** page to draw and save your field boundary.
    2. **Set Veris parameters**: Define date and measurement ranges for EC, pH, etc.
    3. **Generate Veris data**: Click "Make Veris Data" to generate the `.dat` file.
    4. **Download**: Download the generated `.dat` file for import into your application.
    """, unsafe_allow_html=True)

# Helper functions
def get_polygon_bounds(polygon_features):
    polygons = [shapely_shape(feature['geometry']) for feature in polygon_features if feature['geometry']['type'] in ['Polygon', 'MultiPolygon']]
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

def get_field_boundary():
    if st.session_state.uploaded_boundary:
        uploaded_boundary_gdf = gpd.GeoDataFrame.from_features(st.session_state.uploaded_boundary["features"], crs="EPSG:4326")
        if not uploaded_boundary_gdf.empty:
            field_multipolygon = uploaded_boundary_gdf.unary_union
            return field_multipolygon
    if 'saved_geography' in st.session_state and st.session_state.saved_geography:
        features = st.session_state.saved_geography
        polygons = [shapely_shape(feature['geometry']) for feature in features if feature['geometry']['type'] in ['Polygon', 'MultiPolygon']]
        if polygons:
            field_multipolygon = unary_union(polygons)
            return field_multipolygon
    return None

# Set the map's initial location and zoom level based on the saved boundary
if 'saved_geography' in st.session_state and st.session_state.saved_geography:
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
    zoom_start = 5

# Create the map
m = folium.Map(location=location, zoom_start=zoom_start)

# Add boundary to map
if 'saved_geography' in st.session_state and st.session_state.saved_geography:
    for feature in st.session_state.saved_geography:
        if feature['geometry']['type'] in ['Polygon', 'MultiPolygon']:
            folium.GeoJson(
                data=feature,
                style_function=lambda x: {"fillColor": "blue", "color": "blue", "weight": 1, "fillOpacity": 0.3}
            ).add_to(m)
elif st.session_state.uploaded_boundary:
    folium.GeoJson(
        data=st.session_state.uploaded_boundary,
        style_function=lambda x: {"fillColor": "green", "color": "green", "weight": 1, "fillOpacity": 0.3}
    ).add_to(m)
else:
    st.warning("No field boundary found. Please use the **✏️ Draw a Field** page to create and save your field boundary before generating Veris data.")

# Display map and parameters
col1, col2 = st.columns(2)

with col1:
    st_folium(m, width='100%', height=500)

with col2:
    # Veris data parameters
    st.header("Veris Data Parameters")

    survey_date = st.date_input("Survey Date", value=datetime.today())
    num_lines = st.number_input("Number of Survey Lines", min_value=1, max_value=100, value=10)

    ec_range = st.slider("EC Measurement Range (mS/m)", min_value=0.0, max_value=100.0, value=(5.0, 50.0))
    ph_range = st.slider("pH Measurement Range", min_value=4.0, max_value=8.5, value=(5.5, 7.5))

    # Generate Veris data
if st.button("Make Veris Data"):
    field_boundary = get_field_boundary()
    if field_boundary is not None:
        with st.spinner("Generating Veris data..."):
            # Apply a small buffer to handle precision issues
            boundary = field_boundary.buffer(1e-9)
            minx, miny, maxx, maxy = boundary.bounds
            line_spacing = (maxx - minx) / (num_lines + 1)

            lines = []
            for i in range(1, num_lines + 1):
                x = minx + i * line_spacing
                line = LineString([(x, miny), (x, maxy)])
                line = line.intersection(boundary)
                if line.is_empty:
                    continue
                lines.append(line)

            # Log number of lines generated
            st.write(f"Number of survey lines generated: {len(lines)}")

            # Generate points along lines
            points = []
            for line in lines:
                if line.is_empty:
                    continue
                if line.geom_type == 'MultiLineString':
                    for linestring in line:
                        num_points = max(int(linestring.length / 10), 1)
                        for distance in np.linspace(0, linestring.length, num_points):
                            point = linestring.interpolate(distance)
                            if not boundary.covers(point):
                                continue
                            points.append(point)
                elif line.geom_type == 'LineString':
                    num_points = max(int(line.length / 10), 1)
                    for distance in np.linspace(0, line.length, num_points):
                        point = line.interpolate(distance)
                        if not boundary.covers(point):
                            continue
                        points.append(point)

            # Log number of points generated
            st.write(f"Number of points generated: {len(points)}")

            # Check if points were generated
            if len(points) == 0:
                st.error("No sampling points were generated within the field boundary. Please check the boundary and parameters.")
            else:
                # Create DataFrame
                data = {
                    'Latitude': [pt.y for pt in points],
                    'Longitude': [pt.x for pt in points],
                    'EC': np.random.uniform(ec_range[0], ec_range[1], len(points)),
                    'pH': np.random.uniform(ph_range[0], ph_range[1], len(points)),
                    'Date': [survey_date.strftime('%Y-%m-%d')] * len(points),
                    'Time': [(datetime.combine(survey_date, datetime.min.time()) + timedelta(seconds=i*10)).strftime('%H:%M:%S') for i in range(len(points))]
                }
                veris_df = pd.DataFrame(data)
                st.session_state.veris_data = veris_df

                st.success("Veris data generated successfully!")
    else:
        st.error("No field boundary found. Please use the **✏️ Draw a Field** page to create and save your field boundary before generating Veris data.")

# Show generated data and download option
if st.session_state.veris_data is not None:
    st.header("Generated Veris Data Preview")
    st.dataframe(st.session_state.veris_data.head())

    # Download button
    @st.cache_data
    def convert_df(df):
        return df.to_csv(index=False, sep='\t').encode('utf-8')

    veris_dat = convert_df(st.session_state.veris_data)

    st.download_button(
        label="Download Veris .dat File",
        data=veris_dat,
        file_name='veris_data.dat',
        mime='text/plain',
    )
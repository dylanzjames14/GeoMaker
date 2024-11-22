import streamlit as st
import folium
from streamlit_folium import st_folium
from shapely.geometry import Point, Polygon, MultiPolygon, shape as shapely_shape
from shapely.ops import unary_union
import geopandas as gpd
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

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
    2. **Set Veris parameters**: Define date and measurement ranges for EC Shallow, EC Deep, pH, etc.
    3. **Generate Veris data**: Click "Make Veris Data" to generate the `.dat` file.
    4. **Download**: Download the generated `.dat` file for import into your application.
    """, unsafe_allow_html=True)

# Helper functions
def get_field_boundary():
    if st.session_state.uploaded_boundary:
        uploaded_boundary_gdf = gpd.GeoDataFrame.from_features(st.session_state.uploaded_boundary["features"], crs="EPSG:4326")
        if not uploaded_boundary_gdf.empty:
            field_multipolygon = uploaded_boundary_gdf.unary_union
            return field_multipolygon
    if st.session_state.saved_geography:
        features = st.session_state.saved_geography
        polygons = [shapely_shape(feature['geometry']) for feature in features if feature['geometry']['type'] in ['Polygon', 'MultiPolygon']]
        if polygons:
            field_multipolygon = unary_union(polygons)
            return field_multipolygon
    return None

def generate_grid_points(boundary, point_spacing_degrees):
    minx, miny, maxx, maxy = boundary.bounds

    # Generate grid coordinates using numpy
    x_coords = np.arange(minx, maxx, point_spacing_degrees)
    y_coords = np.arange(miny, maxy, point_spacing_degrees)
    xx, yy = np.meshgrid(x_coords, y_coords)
    grid_points = np.c_[xx.ravel(), yy.ravel()]

    # Create a GeoDataFrame of points
    points_gdf = gpd.GeoDataFrame(geometry=gpd.points_from_xy(grid_points[:, 0], grid_points[:, 1]), crs="EPSG:4326")

    # Create a GeoDataFrame for the boundary
    boundary_gdf = gpd.GeoDataFrame(geometry=[boundary], crs="EPSG:4326")

    # Use spatial join to keep only points within the boundary
    points_within_boundary = gpd.sjoin(points_gdf, boundary_gdf, predicate='within', how='inner')

    # Extract points
    points = points_within_boundary.geometry.tolist()

    return points

# Get the field boundary
field_boundary = get_field_boundary()

# Create the map
if field_boundary:
    min_lon, min_lat, max_lon, max_lat = field_boundary.bounds
    center_lat = (min_lat + max_lat) / 2
    center_lon = (min_lon + max_lon) / 2
    location = [center_lat, center_lon]
    zoom_start = 15
else:
    location = [36.1256, -97.0665]
    zoom_start = 5

m = folium.Map(location=location, zoom_start=zoom_start)

# Add boundary to map
if field_boundary:
    folium.GeoJson(
        data=field_boundary.__geo_interface__,
        style_function=lambda x: {"fillColor": "blue", "color": "blue", "weight": 1, "fillOpacity": 0.3}
    ).add_to(m)
else:
    st.warning("No field boundary found. Please use the **✏️ Draw a Field** page to create and save your field boundary before generating Veris data.")

# Veris data parameters
col1, col2 = st.columns(2)

with col2:
    st.header("Veris Data Parameters")

    survey_date = st.date_input("Survey Date", value=datetime.today())
    survey_start_time = st.time_input("Survey Start Time", value=datetime.now().time())
    survey_speed = st.number_input("Survey Speed (meters/second)", min_value=0.1, max_value=10.0, value=5.0)
    ec_shallow_range = st.slider("EC Shallow Measurement Range (mS/m)", min_value=0.0, max_value=100.0, value=(5.0, 50.0))
    ec_deep_range = st.slider("EC Deep Measurement Range (mS/m)", min_value=0.0, max_value=200.0, value=(10.0, 100.0))
    ph_range = st.slider("pH Measurement Range", min_value=4.0, max_value=8.5, value=(5.5, 7.5))

# Display the map
with col1:
    st_folium(m, width='100%', height=500)

# Generate Veris data
if st.button("Make Veris Data"):
    if field_boundary is not None:
        with st.spinner("Generating Veris data..."):
            # Apply a small buffer to handle precision issues
            boundary = field_boundary.buffer(1e-9)

            # Estimate point spacing based on survey speed (meters per second) and desired time interval (1 second)
            point_spacing_meters = survey_speed  # Assuming one point per second

            # Convert point spacing from meters to degrees (approximate)
            # 1 degree ≈ 111,320 meters
            point_spacing_degrees = point_spacing_meters / 111320

            # Generate grid points within the field boundary
            points = generate_grid_points(boundary, point_spacing_degrees)

            # Log number of points generated
            st.write(f"Number of points generated: {len(points)}")

            # Check if points were generated
            if len(points) == 0:
                st.error("No sampling points were generated within the field boundary. Please check the boundary and parameters.")
            else:
                # Create DataFrame
                start_datetime = datetime.combine(survey_date, survey_start_time)
                timestamps = [start_datetime + timedelta(seconds=i) for i in range(len(points))]
                data = {
                    'Latitude': [pt.y for pt in points],
                    'Longitude': [pt.x for pt in points],
                    'EC Shallow': np.random.uniform(ec_shallow_range[0], ec_shallow_range[1], len(points)),
                    'EC Deep': np.random.uniform(ec_deep_range[0], ec_deep_range[1], len(points)),
                    'pH': np.random.uniform(ph_range[0], ph_range[1], len(points)),
                    'Date': [dt.strftime('%Y-%m-%d') for dt in timestamps],
                    'Time': [dt.strftime('%H:%M:%S') for dt in timestamps]
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
    def convert_df(df):
        return df.to_csv(index=False, sep='\t').encode('utf-8')

    veris_dat = convert_df(st.session_state.veris_data)

    st.download_button(
        label="Download Veris .dat File",
        data=veris_dat,
        file_name='veris_data.dat',
        mime='text/plain',
    )

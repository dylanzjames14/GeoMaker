import streamlit as st
import pandas as pd
import geopandas as gpd
import folium
from shapely import wkt
from streamlit_folium import folium_static
from shapely.errors import WKTReadingError
from shapely.geometry import MultiPolygon, Polygon
import pyproj

def compare_geometries(df, wkt_column, label_column):
    start_row = st.slider('Select the start row', min_value=0, max_value=len(df)-1, value=0, step=1)
    num_rows = st.slider('Select the number of rows to process', min_value=1, max_value=min(50, len(df)-start_row), value=5, step=1)

    for i in range(start_row, start_row + num_rows):
        wkt_str = df.loc[i, wkt_column]
        row_label = df.loc[i, label_column] if label_column else None

        try:
            poly = wkt.loads(wkt_str)
            if isinstance(poly, (Polygon, MultiPolygon)):
                display_geometry_stats(poly, f"Row {i+1}" + (f" ({row_label})" if row_label else ""), prefix=wkt_column)
            else:
                st.error(f'Non-Polygon/MultiPolygon geometry in row {i+1} ({row_label}). Please check your inputs.')
        except WKTReadingError:
            st.error(f'Invalid WKT in row {i+1} ({row_label}). Please check your inputs.')

def display_geometry_stats(poly, label, prefix=""):
    if not isinstance(poly, (Polygon, MultiPolygon)):
        st.error('The provided geometry is neither a Polygon nor a MultiPolygon.')
        return

    gdf = gpd.GeoDataFrame(geometry=[poly], crs='EPSG:4326')
    gdf = gdf.to_crs('EPSG:3395')

    total_area = gdf.geometry.area[0]
    total_perimeter = gdf.geometry.length[0]

    m = folium.Map(location=[poly.centroid.y, poly.centroid.x], zoom_start=12)
    folium.GeoJson(poly).add_to(m)

    polygons = []
    if isinstance(poly, Polygon):
        polygons.append(poly)
    elif isinstance(poly, MultiPolygon):
        for geom in poly.geoms:
            polygons.append(geom)

    for polygon in polygons:
        exterior_coords = polygon.exterior.coords.xy
        exterior_coords_df = pd.DataFrame({'lon': exterior_coords[0], 'lat': exterior_coords[1]})
        exterior_coords_gdf = gpd.GeoDataFrame(exterior_coords_df, geometry=gpd.points_from_xy(exterior_coords_df.lon, exterior_coords_df.lat), crs='EPSG:4326')
        exterior_coords_gdf = exterior_coords_gdf.to_crs('EPSG:3395')
        exterior_coords_gdf['shifted'] = exterior_coords_gdf.geometry.shift(-1)
        exterior_coords_gdf = exterior_coords_gdf[:-1]
        exterior_coords_gdf['segment_length'] = exterior_coords_gdf.apply(lambda row: row.geometry.distance(row.shifted), axis=1)
        outer_perimeter = exterior_coords_gdf.segment_length.sum()

        st.subheader(f'Polygon Stats ({label}):')
        st.write(f'Total Area ({prefix}): {total_area:.2f} m²')
        st.write(f'Total Perimeter ({prefix}): {total_perimeter:.2f} meters')
        if outer_perimeter:
            st.write(f'Outer Perimeter ({prefix}): {outer_perimeter:.2f} meters')
        st.write(f'Bounds ({prefix}): {poly.bounds}')
        st.markdown(f'**Polygon Map ({label}):**')
        folium_static(m)

    m = folium.Map(location=[poly.centroid.y, poly.centroid.x], zoom_start=2)
    folium.GeoJson(poly).add_to(m)

    st.subheader(f'Polygon Stats ({label}):')
    st.write(f'Total Area ({prefix}): {total_area:.2f} m²')
    st.write(f'Total Perimeter ({prefix}): {total_perimeter:.2f} meters')
    st.write(f'Outer Perimeter ({prefix}): {outer_perimeter:.2f} meters')
    st.write(f'Bounds ({prefix}): {poly.bounds}')
    st.markdown(f'**Polygon Map ({label}):**')
    folium_static(m)

st.set_page_config(page_title="Geomaker", page_icon="🌍", layout="wide")
st.title('🔎 Compare WKTs')
st.markdown("""
    **Instructions:** Either upload a CSV file and select one or two columns that contain the Well-Known Text (WKT) for the polygons you want to compare,
    or alternatively enter a WKT string directly. If you upload a CSV, you can also select the row label column (optional) and the number of rows to process 
    (up to a maximum of 50). The polygons and their overlapping areas will be displayed on maps, along with their stats.
""")

wkt_source = st.radio("Choose the WKT source", ['Upload CSV', 'Input WKT'], index=0)

if wkt_source == 'Upload CSV':
    uploaded_file = st.file_uploader("Choose a CSV file", type="csv")

    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file)
        wkt_column = st.multiselect('Select WKT column(s)', df.columns, [])
        label_column = st.selectbox('Select the row label column (optional)', ['', *df.columns])

        if len(wkt_column) == 0:
            st.warning('Please select at least one WKT column to proceed.')
        else:
            for wkt_col in wkt_column:
                compare_geometries(df, wkt_col, label_column)

elif wkt_source == 'Input WKT':
    wkt_inputs = st.text_area("Enter one or more WKT strings, separated by a line:", value="", height=150, max_chars=None, key=None)
    wkts = wkt_inputs.split("\\n")

    if wkt_inputs:
        for i, wkt_str in enumerate(wkts):
            try:
                poly = wkt.loads(wkt_str)
                if isinstance(poly, (Polygon, MultiPolygon)):
                    display_geometry_stats(poly, f"WKT {i+1}")
                else:
                    st.error(f'Non-Polygon/MultiPolygon geometry at position {i+1}. Please check your inputs.')
            except WKTReadingError:
                st.error(f'Invalid WKT at position {i+1}. Please check your inputs.')

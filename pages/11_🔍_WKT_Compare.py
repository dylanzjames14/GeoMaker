import streamlit as st
import geopandas as gpd
import folium
from shapely import wkt
from streamlit_folium import folium_static
from shapely.errors import WKTReadingError
from shapely.geometry import MultiPolygon

# Setup Streamlit layout
st.set_page_config(layout="wide")
st.title('🔍 Compare WKTs')
st.markdown("""
    **Instructions:** Paste the Well-Known Text (WKT) for each of the polygons you want to compare in the boxes below.
    The polygons will be displayed on a map, and you will receive statistics for each, including area, perimeter, and extent.
""")

# Create two columns for user input
col1, col2 = st.columns(2)

# Get WKT from user
with col1:
    st.markdown('**🔵 Polygon 1:**')
    wkt1 = st.text_area('Paste your first WKT here')

with col2:
    st.markdown('**🔴 Polygon 2:**')
    wkt2 = st.text_area('Paste your second WKT here')

# Create polygons from WKT and calculate stats
if wkt1 and wkt2:
    try:
        poly1 = wkt.loads(wkt1)
        poly2 = wkt.loads(wkt2)
    except WKTReadingError:
        st.error('Invalid WKT. Please check your inputs.')
        st.stop()

    if isinstance(poly1, MultiPolygon):
        polys1 = [poly for poly in poly1.geoms]
    else:
        polys1 = [poly1]

    if isinstance(poly2, MultiPolygon):
        polys2 = [poly for poly in poly2.geoms]
    else:
        polys2 = [poly2]

    # Create a GeoSeries from the polygons
    gdf = gpd.GeoSeries(polys1 + polys2)

    # Get the max extents
    max_bounds = gdf.total_bounds

    # Create folium map centered on the polygons and zoomed on the extents
    m = folium.Map(location=[gdf.centroid.y.mean(), gdf.centroid.x.mean()], zoom_start=15, control_scale=True)

    # Add polygons to the map with different colors and narrower borders
    for idx, poly in enumerate(polys1):
        folium.GeoJson(poly, name=f"Polygon 1-{idx + 1}",
                       style_function=lambda x: {'fillColor': 'red', 'color': 'red', 'weight': 1}).add_to(m)

    for idx, poly in enumerate(polys2):
        folium.GeoJson(poly, name=f"Polygon 2-{idx + 1}",
                       style_function=lambda x: {'fillColor': 'blue', 'color': 'blue', 'weight': 1}).add_to(m)

    # Fit map to max extents
    m.fit_bounds([[max_bounds[1], max_bounds[0]], [max_bounds[3], max_bounds[2]]])

    folium_static(m)

    # Calculate stats for each polygon
    with col1:
        st.subheader('Polygon 1 Stats:')
        for idx, poly in enumerate(polys1):
            st.write(f'Area 1-{idx + 1} (m²): {poly.area}')
            st.write(f'Perimeter 1-{idx + 1} (m): {poly.length}')
            st.write(f'Bounds 1-{idx + 1}: {poly.bounds}')

    with col2:
        st.subheader('Polygon 2 Stats:')
        for idx, poly in enumerate(polys2):
            st.write(f'Area 2-{idx + 1} (m²): {poly.area}')
            st.write(f'Perimeter 2-{idx + 1} (m): {poly.length}')
            st.write(f'Bounds 2-{idx + 1}: {poly.bounds}')

    # Compare polygons' stats
    st.subheader('Comparison of polygons')
    for idx in range(max(len(polys1), len(polys2))):
        poly1 = polys1[idx] if idx < len(polys1) else None
        poly2 = polys2[idx] if idx < len(polys2) else None
        if poly1 and poly2:
            st.write(f'Difference in area {idx + 1} (m²): {abs(poly1.area - poly2.area)}')
            st.write(f'Difference in perimeter {idx + 1} (m): {abs(poly1.length - poly2.length)}')
            st.write(f'Difference in extent {idx + 1}: {abs(poly1.bounds[2] - poly2.bounds[2])} m in x direction, {abs(poly1.bounds[3] - poly2.bounds[3])} m in y direction')
        else:
            st.write(f"Polygon {idx + 1} does not exist in both groups.")

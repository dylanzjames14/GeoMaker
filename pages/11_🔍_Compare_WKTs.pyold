import streamlit as st
import geopandas as gpd
import folium
from shapely import wkt
from streamlit_folium import folium_static
from shapely.errors import WKTReadingError
from shapely.geometry import MultiPolygon
import pyproj

# Setup Streamlit layout
st.set_page_config(page_title="Geomaker", page_icon="🌍", layout="wide")
st.title('🔎 Compare WKTs')
st.markdown("""
    **Instructions:** Paste the Well-Known Text (WKT) for each of the polygons you want to compare in the boxes below.
    The polygons will be displayed on two maps, one for each polygon and the overlapping area.
""")
with st.expander("Information about the metrics"):
    st.write("""
    - **Total Area**: The total area of the polygon, calculated in square meters (m²). This is calculated by summing the areas of all individual polygons if a MultiPolygon is provided.
    
    - **Total Perimeter**: The total length of the boundary of the polygon, calculated in meters. If a MultiPolygon is provided, this is calculated by summing the lengths of the boundaries of all individual polygons.
    
    - **Outer Perimeter**: The length of the outer boundary of the polygon, calculated in meters. If a MultiPolygon is provided, this is the length of the boundary of the union of all individual polygons.
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

    # Determine UTM Zone
    centroid = polys1[0].centroid  # Use the first polygon to determine UTM zone
    utm_zone = int((centroid.x + 180) / 6) + 1
    utm_crs = f"+proj=utm +zone={utm_zone} +ellps=WGS84 +datum=WGS84 +units=m +no_defs"

    # Create a GeoSeries from the polygons
    gdf = gpd.GeoSeries(polys1 + polys2).set_crs("EPSG:4326")

    # Project to UTM CRS for accurate measurements
    gdf_utm = gdf.to_crs(utm_crs)

    # Get the max extents
    max_bounds = gdf.total_bounds

    # Create individual folium maps for each polygon
    m1_poly1 = folium.Map(location=[gdf.centroid.y.mean(), gdf.centroid.x.mean()], zoom_start=15, control_scale=True)
    m1_poly2 = folium.Map(location=[gdf.centroid.y.mean(), gdf.centroid.x.mean()], zoom_start=15, control_scale=True)

    # Add polygons to their respective maps
    for idx, poly in enumerate(polys1):
        folium.GeoJson(poly, name=f"Polygon 1-{idx + 1}",
                       style_function=lambda x: {'fillColor': 'red', 'color': 'red', 'weight': 1}).add_to(m1_poly1)

    for idx, poly in enumerate(polys2):
        folium.GeoJson(poly, name=f"Polygon 2-{idx + 1}",
                       style_function=lambda x: {'fillColor': 'blue', 'color': 'blue', 'weight': 1}).add_to(m1_poly2)

    # Calculate total area, total and outer perimeter for each WKT
    total_area_1 = sum([poly.area for poly in gdf_utm[:len(polys1)]])
    total_perimeter_1 = sum([poly.length for poly in gdf_utm[:len(polys1)]])
    outer_perimeter_1 = gpd.GeoSeries(gdf_utm[:len(polys1)]).unary_union.boundary.length
    total_area_2 = sum([poly.area for poly in gdf_utm[len(polys1):]])
    total_perimeter_2 = sum([poly.length for poly in gdf_utm[len(polys1):]])
    outer_perimeter_2 = gpd.GeoSeries(gdf_utm[len(polys1):]).unary_union.boundary.length

    # Display total area, total and outer perimeter for each WKT and their respective map
    with col1:
        st.subheader('🔵 Polygon 1 Stats:')
        st.write(f'Total Area 1 (m²): {total_area_1:.2f} m²')
        st.write(f'Total Perimeter 1 (meters): {total_perimeter_1:.2f} meters')
        st.write(f'Outer Perimeter 1 (meters): {outer_perimeter_1:.2f} meters')
        st.write(f'Bounds 1: {poly1.bounds}')
        st.markdown('**🔵 Polygon 1 Map:**')
        folium_static(m1_poly1)

    with col2:
        st.subheader('🔴 Polygon 2 Stats:')
        st.write(f'Total Area 2 (m²): {total_area_2:.2f} m²')
        st.write(f'Total Perimeter 2 (meters): {total_perimeter_2:.2f} meters')
        st.write(f'Outer Perimeter 2 (meters): {outer_perimeter_2:.2f} meters')
        st.write(f'Bounds 2: {poly2.bounds}')
        st.markdown('**🔴 Polygon 2 Map:**')
        folium_static(m1_poly2)

    # Create folium map for the overlay of polygons
    m1 = folium.Map(location=[gdf.centroid.y.mean(), gdf.centroid.x.mean()], zoom_start=15, control_scale=True)

    # Add polygons to the map with different colors and narrower borders
    for idx, poly in enumerate(polys1):
        folium.GeoJson(poly, name=f"Polygon 1-{idx + 1}",
                       style_function=lambda x: {'fillColor': 'red', 'color': 'red', 'weight': 1}).add_to(m1)

    for idx, poly in enumerate(polys2):
        folium.GeoJson(poly, name=f"Polygon 2-{idx + 1}",
                       style_function=lambda x: {'fillColor': 'blue', 'color': 'blue', 'weight': 1}).add_to(m1)

    # Fit map to max extents
    m1.fit_bounds([[max_bounds[1], max_bounds[0]], [max_bounds[3], max_bounds[2]]])

    # Create folium map for the overlapping area
    m2 = folium.Map(location=[gdf.centroid.y.mean(), gdf.centroid.x.mean()], zoom_start=15, control_scale=True)

    # Add overlapping area to the map
    for idx1, poly1 in enumerate(polys1):
        for idx2, poly2 in enumerate(polys2):
            intersection = poly1.intersection(poly2)
            if intersection.is_empty:
                st.write(f"No intersection between Polygon 1-{idx1 + 1} and Polygon 2-{idx2 + 1}")
            else:
                folium.GeoJson(intersection, name=f"Intersection of Polygon 1-{idx1 + 1} and Polygon 2-{idx2 + 1}",
                               style_function=lambda x: {'fillColor': 'green', 'color': 'green', 'weight': 1}).add_to(m2)

    # Fit map to max extents
    m2.fit_bounds([[max_bounds[1], max_bounds[0]], [max_bounds[3], max_bounds[2]]])

    # Display overlay and overlapping maps side by side
    col1, col2 = st.columns(2)
    with col1:
        st.markdown('**🔵🔴 Overlay of Polygon 1 and 2:**')
        folium_static(m1)
    with col2:
        st.markdown('**🟢 Overlapping Area of Polygon 1 and 2:**')
        folium_static(m2)

    # Compare polygons' stats
    st.subheader('Comparison of polygons')
    area_diff = abs(total_area_1 - total_area_2) / max(total_area_1, total_area_2) * 100
    st.write(f'Difference in total area (%): {area_diff:.2f}%')
    
    perimeter_diff = abs(total_perimeter_1 - total_perimeter_2) / max(total_perimeter_1, total_perimeter_2) * 100
    st.write(f'Difference in total perimeter (%): {perimeter_diff:.2f}%')
    
    outer_perimeter_diff = abs(outer_perimeter_1 - outer_perimeter_2) / max(outer_perimeter_1, outer_perimeter_2) * 100
    st.write(f'Difference in outer perimeter (%): {outer_perimeter_diff:.2f}%')

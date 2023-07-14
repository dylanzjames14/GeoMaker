import streamlit as st
import geopandas as gpd
import folium
from shapely import wkt
from streamlit_folium import folium_static
from shapely.errors import WKTReadingError

# Setup Streamlit layout
st.set_page_config(layout="wide")
st.title('Compare Two WKT Polygons')
st.markdown("""
    **Instructions:** Paste the Well-Known Text (WKT) for each of the polygons you want to compare in the boxes below.
    The polygons will be displayed on a map, and you will receive statistics for each, including area, perimeter, and extent.
""")

# Create two columns for user input
col1, col2 = st.columns(2)

# Get WKT from user
with col1:
    st.markdown('**Polygon 1 (Red):**')
    wkt1 = st.text_area('Paste your first WKT here')

with col2:
    st.markdown('**Polygon 2 (Blue):**')
    wkt2 = st.text_area('Paste your second WKT here')

# Create polygons from WKT and calculate stats
if wkt1 and wkt2:
    try:
        poly1 = wkt.loads(wkt1)
        poly2 = wkt.loads(wkt2)
    except WKTReadingError:
        st.error('Invalid WKT. Please check your inputs.')
        st.stop()

    # Create a GeoSeries from the polygons
    gdf = gpd.GeoSeries([poly1, poly2])
    
    # Get the max extents
    max_bounds = gdf.total_bounds

    # Create folium map centered on the polygons and zoomed on the extents
    m = folium.Map(location=[gdf.centroid.y.mean(), gdf.centroid.x.mean()], zoom_start=15, control_scale=True)

    # Add polygons to the map with different colors
    folium.GeoJson(poly1, name="Polygon 1", 
                   style_function=lambda x: {'fillColor': 'red', 'color': 'black'}).add_to(m)
    folium.GeoJson(poly2, name="Polygon 2", 
                   style_function=lambda x: {'fillColor': 'blue', 'color': 'black'}).add_to(m)

    # Fit map to max extents
    m.fit_bounds([[max_bounds[1], max_bounds[0]], [max_bounds[3], max_bounds[2]]])

    folium_static(m)

    # Calculate stats for each polygon
    with col1:
        st.subheader('Polygon 1 Stats:')
        st.write('Area 1 (m²): {}'.format(poly1.area))
        st.write('Perimeter 1 (m): {}'.format(poly1.length))
        st.write('Bounds 1: {}'.format(poly1.bounds))

    with col2:
        st.subheader('Polygon 2 Stats:')
        st.write('Area 2 (m²): {}'.format(poly2.area))
        st.write('Perimeter 2 (m): {}'.format(poly2.length))
        st.write('Bounds 2: {}'.format(poly2.bounds))

    # Compare polygons' stats
    st.subheader('Comparison of polygons')
    st.write('Difference in area (m²): {}'.format(abs(poly1.area - poly2.area)))
    st.write('Difference in perimeter (m): {}'.format(abs(poly1.length - poly2.length)))
    st.write('Difference in extent: {} m in x direction, {} m in y direction'.format(
        abs(poly1.bounds[2] - poly2.bounds[2]), abs(poly1.bounds[3] - poly2.bounds[3])))

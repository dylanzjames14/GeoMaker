import streamlit as st
import pandas as pd
import geopandas as gpd
import folium
from shapely import wkt
from streamlit_folium import folium_static
from shapely.errors import WKTReadingError
from shapely.geometry import MultiPolygon
import pyproj
import io

# Setup Streamlit layout
st.set_page_config(page_title="Spatial Annihilator", page_icon="🌍", layout="wide")
st.title('🗺️ WKT Analyzer')
st.write('Welcome to WKT Analyzer! A tool for visualizing and dissecting Well-Known Text (WKT). This page simplifies your geospatial analysis by offering an easy upload-and-compare feature for multiple WKTs.')

with st.expander("📝 Instructions"):
    st.markdown("""
    **Step 1:** Upload a CSV or Excel file that contains Well-Known Text (WKT) for polygons.
    
    **Step 2:** Select the columns containing the WKTs and identifiers.
    
    **Step 3:** Choose the starting row and number of rows to process (max 500 rows).
    
    **Step 4:** Sit back and enjoy as your polygons and their overlaps are visualized on maps with statistics provided.
    """)

# File uploader
uploaded_file = st.file_uploader("Select a file", type=["csv", "xlsx", "dbf"])

if uploaded_file is not None:
    # Load the file
    if uploaded_file.type == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet":
        df = pd.read_excel(uploaded_file)
    elif uploaded_file.type == "application/x-dbf":
        df = gpd.read_file(uploaded_file)
    else:  # Assume it's a CSV
        df = pd.read_csv(uploaded_file)

    # Selectors for the WKT columns and the identifier column
    wkt_columns = st.multiselect('Select the WKT columns', df.columns, default=df.columns[:2].tolist())
    id_column = st.selectbox('Select an identifier column', df.columns)

    # Sliders to select the start row and the number of rows to process
    start_row = st.slider('Start row', min_value=0, max_value=len(df)-1, value=0, step=1)
    num_rows = st.slider('Number of rows to process', min_value=1, max_value=min(500, len(df)-start_row), value=5, step=1)

    # Loop through the selected rows
    for i in range(start_row, start_row + num_rows):
        # Get the WKT strings and the row identifier
        wkts = [df.loc[i, col] for col in wkt_columns]
        row_identifier = df.loc[i, id_column]

        st.subheader(f'Row Identifier: {row_identifier}')

        # Create polygons from WKT and calculate stats
        polys = []
        maps = []
        total_areas = []
        total_perimeters = []
        outer_perimeters = []

        for j, wkt_str in enumerate(wkts):
            if wkt_str:
                try:
                    poly = wkt.loads(wkt_str)
                except WKTReadingError:
                    st.error('Invalid WKT. Please check your inputs.')
                    st.stop()

                if isinstance(poly, MultiPolygon):
                    polys.append([p for p in poly.geoms])
                else:
                    polys.append([poly])

                # Determine UTM Zone
                centroid = polys[j][0].centroid  # Use the first polygon to determine UTM zone
                utm_zone = int((centroid.x + 180) / 6) + 1
                utm_crs = f"+proj=utm +zone={utm_zone} +ellps=WGS84 +datum=WGS84 +units=m +no_defs"

                # Create a GeoSeries from the polygons
                gdf = gpd.GeoSeries(polys[j]).set_crs("EPSG:4326")

                # Project to UTM CRS for accurate measurements
                gdf_utm = gdf.to_crs(utm_crs)

                # Get the max extents
                max_bounds = gdf.total_bounds

                # Create individual folium maps for each polygon
                m = folium.Map(location=[gdf.centroid.y.mean(), gdf.centroid.x.mean()], zoom_start=15, control_scale=True)
                maps.append(m)

                # Add polygons to their respective maps
                for idx, p in enumerate(polys[j]):
                    folium.GeoJson(p, name=f"{wkt_columns[j]}-{idx + 1}",
                                   style_function=lambda x: {'fillColor': 'blue', 'color': 'blue', 'weight': 1}).add_to(maps[j])

                # Calculate total area, total and outer perimeter for each WKT
                total_area = sum([p.area for p in gdf_utm])
                total_perimeter = sum([p.length for p in gdf_utm])
                outer_perimeter = gpd.GeoSeries(gdf_utm).unary_union.boundary.length

                total_areas.append(total_area)
                total_perimeters.append(total_perimeter)
                outer_perimeters.append(outer_perimeter)

        # Display total area, total and outer perimeter for each WKT and their respective map
        for j in range(len(wkts)):
            if j == 0:  # first column
                col1, col2 = st.columns(2)
                with col1:
                    st.subheader(f'🔵 {wkt_columns[j]} Stats:')
                    st.write(f'Total Area {j+1} (m²): {total_areas[j]:.2f} m²')
                    st.write(f'Total Perimeter {j+1} (meters): {total_perimeters[j]:.2f} meters')
                    st.write(f'Outer Perimeter {j+1} (meters): {outer_perimeters[j]:.2f} meters')
                    st.write(f'Bounds {j+1}: {polys[j][0].bounds}')
                    st.markdown(f'**🔵 {wkt_columns[j]} Map:**')
                    folium_static(maps[j])
            else:  # second column
                with col2:
                    st.subheader(f'🔴 {wkt_columns[j]} Stats:')
                    st.write(f'Total Area {j+1} (m²): {total_areas[j]:.2f} m²')
                    st.write(f'Total Perimeter {j+1} (meters): {total_perimeters[j]:.2f} meters')
                    st.write(f'Outer Perimeter {j+1} (meters): {outer_perimeters[j]:.2f} meters')
                    st.write(f'Bounds {j+1}: {polys[j][0].bounds}')
                    st.markdown(f'**🔴 {wkt_columns[j]} Map:**')
                    folium_static(maps[j])


        # Compare polygons' stats if there are more than one
        if len(wkts) > 1:
            # Create folium map for the overlay of polygons
            m1 = folium.Map(location=[gdf.centroid.y.mean(), gdf.centroid.x.mean()], zoom_start=15, control_scale=True)

            # Add polygons to the map with different colors and narrower borders
            for idx, poly in enumerate(polys[0]):
                folium.GeoJson(poly, name=f"{wkt_columns[0]}-{idx + 1}",
                               style_function=lambda x: {'fillColor': 'blue', 'color': 'blue', 'weight': 1}).add_to(m1)
            
            for idx, poly in enumerate(polys[1]):
                folium.GeoJson(poly, name=f"{wkt_columns[1]}-{idx + 1}",
                               style_function=lambda x: {'fillColor': 'red', 'color': 'red', 'weight': 1}).add_to(m1)

            # Fit map to max extents
            m1.fit_bounds([[max_bounds[1], max_bounds[0]], [max_bounds[3], max_bounds[2]]])

            # Create folium map for the overlapping area
            m2 = folium.Map(location=[gdf.centroid.y.mean(), gdf.centroid.x.mean()], zoom_start=15, control_scale=True)

            # Add overlapping area to the map
            if len(wkt_columns) == 2:
                for idx1, poly1 in enumerate(polys[0]):
                    for idx2, poly2 in enumerate(polys[1]):
                        intersection = poly1.intersection(poly2)
                        if intersection.is_empty:
                            st.write(f"No intersection between {wkt_columns[0]}-{idx1 + 1} and {wkt_columns[1]}-{idx2 + 1}")
                        else:
                            folium.GeoJson(intersection, name=f"Intersection of {wkt_columns[0]}-{idx1 + 1} and {wkt_columns[1]}-{idx2 + 1}",
                                        style_function=lambda x: {'fillColor': 'green', 'color': 'green', 'weight': 1}).add_to(m2)

                # Fit map to max extents
                m2.fit_bounds([[max_bounds[1], max_bounds[0]], [max_bounds[3], max_bounds[2]]])

                # Display overlay and overlapping maps side by side
                col3, col4 = st.columns(2)

                with col3:
                    st.markdown(f'**🔵🔴 Overlay of {wkt_columns[0]} and {wkt_columns[1]}:**')
                    folium_static(m1)

                with col4:
                    st.markdown(f'**🟢 Overlapping Area of {wkt_columns[0]} and {wkt_columns[1]}:**')
                    folium_static(m2)

                # Compare polygons' stats
                st.subheader('Comparison of polygons')
                area_diff = abs(total_areas[0] - total_areas[1]) / max(total_areas) * 100
                st.write(f'Difference in total area (%): {area_diff:.2f}%')

                perimeter_diff = abs(total_perimeters[0] - total_perimeters[1]) / max(total_perimeters) * 100
                st.write(f'Difference in total perimeter (%): {perimeter_diff:.2f}%')

                outer_perimeter_diff = abs(outer_perimeters[0] - outer_perimeters[1]) / max(outer_perimeters) * 100
                st.write(f'Difference in outer perimeter (%): {outer_perimeter_diff:.2f}%')


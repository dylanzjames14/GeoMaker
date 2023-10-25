import folium
import streamlit as st
from folium.plugins import Draw
from streamlit_folium import st_folium

st.set_page_config(layout="wide")

# Title
st.title("MapNow 🗺️")

# Warning: Work in Progress
st.warning("🚧 Work in Progress 🚧")

# Expander for Instructions and Welcome Message
with st.expander("Instructions & Welcome Message", expanded=False):
    st.write("""
    Welcome to the Field Boundary Drawer! 
    Here, you can outline fields on the map and specify details for each drawn field.
    """)
    
    st.markdown("### Instructions:")
    st.markdown("""
    1. **Draw a field boundary** on the map.
    2. Once drawn, the boundary will appear below the map with inputs to specify details.
    3. Use the color picker to choose a color for the field boundary. 
    4. Provide details in the "Grower", "Farm", and "Field" inputs.
    5. To clear all fields and start fresh, click the "Clear all polygons" button.
    """)

# Initial location
location = [36.1256, -97.0665]

# Initialize the map
m = folium.Map(
    location=location,
    zoom_start=11,
    tiles="https://mt1.google.com/vt/lyrs=y@18&x={x}&y={y}&z={z}",
    attr="Google"
)

draw_options = {
    "position": "topleft",
    "polyline": False,
    "circle": False,
    "rectangle": True,
    "polygon": True,
    "circlemarker": False,
    "marker": False
}

draw_control = Draw(draw_options=draw_options)
draw_control.add_to(m)

# Check if 'drawn_geometries' exists in session state, if not initialize it
if 'drawn_geometries' not in st.session_state:
    st.session_state.drawn_geometries = []

# Display the map and capture any drawn geometries
returned_objects = st_folium(m, width='100%', height=650)

# If there are any returned drawn geometries, add them to the session state
if returned_objects and 'all_drawings' in returned_objects and returned_objects['all_drawings']:
    for feature in returned_objects['all_drawings']:
        if isinstance(feature, dict) and 'geometry' in feature:
            existing_geometries = [entry['geometry'] for entry in st.session_state.drawn_geometries if 'geometry' in entry]
            if feature['geometry'] not in existing_geometries:
                st.session_state.drawn_geometries.append({
                    'geometry': feature['geometry'],
                    'color': '#000000',  # default color
                    'grower': '',
                    'farm': '',
                    'field': ''
                })

# Button to clear all polygons
if st.button("Clear all polygons"):
    st.session_state.drawn_geometries = []

# Display the list of drawn geometries below the map
for idx, geo_entry in enumerate(st.session_state.drawn_geometries):
    if 'geometry' in geo_entry:
        col1, col2, col3, col4, col5 = st.columns(5)
        with col1:
            st.subheader(f"Polygon {idx+1}")
        with col2:
            geo_entry['color'] = st.color_picker("Pick a color", geo_entry.get('color', '#000000'))
        with col3:
            geo_entry['grower'] = st.text_input(f"Grower", geo_entry.get('grower', ''))
        with col4:
            geo_entry['farm'] = st.text_input(f"Farm", geo_entry.get('farm', ''))
        with col5:
            geo_entry['field'] = st.text_input(f"Field", geo_entry.get('field', ''))

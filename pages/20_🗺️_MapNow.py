import folium
import streamlit as st
from folium.plugins import Draw
from streamlit_folium import st_folium
from shapely.geometry import shape, mapping

# Check if the page has just been loaded
if not st.session_state.get('initialized'):
    # Clear/reset session state variables
    st.session_state.drawn_geometries = []
    st.session_state.drawn_markers = []
    st.session_state.legend_entries = {}
    # Mark the app as initialized
    st.session_state.initialized = True

st.set_page_config(layout="wide")

# Title
st.title("MapNow 🗺️")

# Warning: Work in Progress
st.warning("🚧 Work in Progress 🚧")

# Expander for Instructions and Welcome Message
with st.expander("Instructions & Welcome Message", expanded=False):
    st.write("""
    Welcome to MapNow! 
    Here, you can outline fields and place markers on the map, then specify details for each.
    """)

    st.markdown("### Instructions:")
    st.markdown("""
    1. **Draw a field boundary or place a marker** on the map.
    2. Once drawn or placed, the boundary/marker will appear below the map with inputs to specify details.
    3. Use the color picker to choose a color for the field boundary or marker.
    4. For fields, provide details in the "Grower", "Farm", and "Field" inputs.
    5. For markers, provide a label.
    6. To clear all fields and markers and start fresh, click the "Clear all" button.
    """)

# Initialize session state for legend entries if not already present
if 'legend_entries' not in st.session_state:
    st.session_state.legend_entries = {}


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
    "marker": True  
}

draw_control = Draw(draw_options=draw_options)
draw_control.add_to(m)

returned_objects = st_folium(m, width='100%', height=650)

# If there are any returned drawn geometries, add them to the session state
if returned_objects and 'all_drawings' in returned_objects and returned_objects['all_drawings']:
    for feature in returned_objects['all_drawings']:
        if feature['geometry']['type'] == 'Polygon':
            existing_geometries = [entry['geometry'] for entry in st.session_state.drawn_geometries if 'geometry' in entry]
            if feature['geometry'] not in existing_geometries:
                st.session_state.drawn_geometries.append({
                    'geometry': feature['geometry'],
                    'color': '#FFFFFF',
                    'grower': '',
                    'farm': '',
                    'field': ''
                })
        elif feature['geometry']['type'] == 'Point':
            existing_markers = [entry['geometry'] for entry in st.session_state.drawn_markers if 'geometry' in entry]
            if feature['geometry'] not in existing_markers:
                st.session_state.drawn_markers.append({
                    'geometry': feature['geometry'],
                    'color': '#FFFFFF',
                    'label': ''
                })

# Button to reset everything
if st.button("Reset all"):
    st.session_state.drawn_geometries = []
    st.session_state.drawn_markers = []

# Separator
st.markdown("---")

# New Report Title Section
st.subheader("Report Title")
report_title = st.text_input("", value="Enter your report title here")

# Separator
st.markdown("---")

# Display the Fields
st.subheader("Fields")

# Display the list of drawn geometries below the map
for idx, geo_entry in enumerate(st.session_state.drawn_geometries):
    if 'geometry' in geo_entry:
        col1, col2, col3, col4, col5 = st.columns(5)
        with col1:
            st.write(f"Field {idx+1}")
        with col2:
            geo_entry['color'] = st.color_picker("Pick a color", geo_entry.get('color', '#000000'), key=f"color_picker_{idx}")
        with col3:
            geo_entry['grower'] = st.text_input(f"Grower", geo_entry.get('grower', ''), key=f"grower_input_{idx}")
        with col4:
            geo_entry['farm'] = st.text_input(f"Farm", geo_entry.get('farm', ''), key=f"farm_input_{idx}")
        with col5:
            geo_entry['field'] = st.text_input(f"Field", geo_entry.get('field', ''), key=f"field_input_{idx}")
        with st.expander("View Details"):
            s = shape(geo_entry['geometry'])
            st.write(s)
            centroid = s.centroid
            st.write(f"Centroid: {centroid.x}, {centroid.y}")

# Separator
st.markdown("---")

# Display the Map Labels
st.subheader("Map Labels")

# Display the list of drawn markers below the drawn geometries
for idx, marker_entry in enumerate(st.session_state.drawn_markers):
    if 'geometry' in marker_entry:
        col1, col2, col3, col4, col5 = st.columns(5)
        with col1:
            st.write(f"Map Label {idx+1}")
        with col2:
            marker_entry['color'] = st.color_picker("Pick a color", marker_entry.get('color', '#000000'), key=f"marker_color_picker_{idx}")
        with col3:
            marker_entry['label'] = st.text_input(f"Label", marker_entry.get('label', ''), key=f"marker_label_input_{idx}")
        with st.expander("View Coordinates"):
            st.write(f"Lat: {marker_entry['geometry']['coordinates'][1]}, Lon: {marker_entry['geometry']['coordinates'][0]}")

# Collect all the colors used in geometries and markers
all_colors = set([geo_entry['color'] for geo_entry in st.session_state.drawn_geometries])
all_colors.update([marker_entry['color'] for marker_entry in st.session_state.drawn_markers])

# Separator
st.markdown("---")

# Display the legend at the bottom of the page
st.subheader("Legend")

# Check and prompt for descriptions of new colors
for color in all_colors:
    if color not in st.session_state.legend_entries:
        # Display a colored block with an input next to it
        st.markdown(f"<div style='display: inline-block; margin-right: 10px; vertical-align: middle;'><span style='display: inline-block; width: 25px; height: 25px; background-color: {color}; margin-right: 5px;'></span></div>", unsafe_allow_html=True)
        description = st.text_input(f"Label for color {color}", key=f"legend_description_{color}")
        if description:
            st.session_state.legend_entries[color] = description
    else:
        # If color already has a description, display it
        st.markdown(f"<div style='display: inline-block; margin-right: 10px;'><span style='display: inline-block; width: 25px; height: 25px; background-color: {color}; margin-right: 5px;'></span>{st.session_state.legend_entries[color]}</div>", unsafe_allow_html=True)

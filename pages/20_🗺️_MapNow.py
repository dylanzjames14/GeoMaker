from streamlit_folium import st_folium
import folium
import streamlit as st
from folium.plugins import Draw
from streamlit_folium import folium_static
from shapely.geometry import shape
from datetime import date
import uuid

def reset_session_state():
    st.session_state.field_id = 1
    st.session_state.label_id = 1
    st.session_state.next_id = 0
    st.session_state.field_maps = {}
    st.session_state.marker_maps = {}
    st.session_state.legend_entries = {}

st.set_page_config(layout="wide")

# Assign keys to all buttons
add_field_key = "add_field"
add_label_key = "add_label"
reset_top_key = "reset_top"
reset_bottom_key = "reset_bottom"

# Initialize session state for field areas
if 'field_total_areas' not in st.session_state:
    st.session_state.field_total_areas = {}

# Initialize session state for separate counters for fields and labels
if 'initialized' not in st.session_state:
    st.session_state.initialized = True
if 'field_id' not in st.session_state:
    st.session_state.field_id = 1
if 'label_id' not in st.session_state:
    st.session_state.label_id = 1


# Initialize session state
if 'next_id' not in st.session_state:
    st.session_state.next_id = 0  # Unique ID generator
if 'field_maps' not in st.session_state:
    st.session_state.field_maps = {}
if 'marker_maps' not in st.session_state:
    st.session_state.marker_maps = {}
if 'legend_entries' not in st.session_state:
    st.session_state.legend_entries = {}


st.title("MapNow 🗺️")

st.markdown("""
Welcome to **MapNow**! This interactive tool allows you to  add fields and markers on a map, customize their details, and generate MapNow report JSON.
""")

# Instructions in an Expander
with st.expander("How to Use", expanded=False):
    st.markdown("""
    - **Add Fields**: Click on 'Add Field' to place a new field on the map. You can define its area, color, and other details.
    - **Add Markers**: Use the 'Add Marker' button to drop markers on the map for specific locations.
    - **Customize Legends**: Each field color can have a legend entry. Add a label to describe what each color represents.
    - **Generate Report**: After setting up your fields and markers, the 'Generated JSON' section will display the report data in JSON format.
    """)
    st.write("Feel free to explore and interact with the map. Please note that there may be some bugs as we continually work to improve this tool. Enjoy mapping!")

# Modify the create_map function
def create_map(map_type, key):
    folium_map = folium.Map(
        location=[36.1256, -97.0665],
        zoom_start=11,
        tiles="https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}",
        attr="Google"
    )
    
    draw_options = {
        "position": "topleft",
        "polyline": False,
        "circle": False,
        "rectangle": True if map_type == 'field' else False,
        "polygon": True if map_type == 'field' else False,
        "circlemarker": False,
        "marker": True if map_type == 'marker' else False  
    }

    draw_control = Draw(draw_options=draw_options)
    draw_control.add_to(folium_map)
    return folium_map

# Function to calculate the area of a polygon
def calculate_area(polygon):
    geom = shape(polygon)
    area_acres = geom.area * (10**4) * 247.105
    return area_acres

# Report Metadata
st.subheader("Report Metadata")
if st.button("Reset all", key=reset_top_key):
    reset_session_state()
col1, col2, col3, col4 = st.columns(4)
with col1:
    report_title = st.text_input("Report title:", key="report_title")
with col2:
    grower = st.text_input("Grower name:", key="grower")
with col3:
    printed_on = st.date_input("Printed on:", value=date.today(), key="printed_on")
with col4:
    printed_by = st.text_input("Printed by:", key="printed_by")

# Section for Fields
st.markdown("---")  
st.subheader("Fields")

fields_data = []  # Initialize the list to hold field data

if st.button("Add Field", key=add_field_key):
    field_key = f'field_{st.session_state.field_id}'
    st.session_state.field_id += 1
    st.session_state.field_total_areas[field_key] = 0  # Initialize total area for this new field
    new_map = create_map('field', field_key)
    st.session_state.field_maps[field_key] = {'map': new_map, 'details': {'color': '#FFFFFF', 'area': '0 acres', 'geometry': None}}

for key, value in st.session_state.field_maps.items():
    if key.startswith("field_"):
        with st.expander(f"Field {key.split('_')[1]}"):
            cols = st.columns((1, 2, 2, 1))

            color = cols[0].color_picker("Color", value['details']['color'], key=f"color_field_{key}")
            farm = cols[1].text_input("Farm", key=f"farm_{key}")
            field_name = cols[2].text_input("Field", key=f"field_{key}")
            STR = cols[3].text_input("STR", key=f"STR_{key}")

            # Folium map with st_folium, using a unique key
            returned_objects = st_folium(value['map'], width=700, height=450, key=f"map_{key}")

            # Check and recalculate the total area for this field
            if returned_objects and 'all_drawings' in returned_objects and returned_objects['all_drawings']:
                st.session_state.field_total_areas[key] = 0  # Reset total area
                for feature in returned_objects['all_drawings']:
                    if feature['geometry']['type'] == 'Polygon':
                        value['details']['geometry'] = feature['geometry']  # Store geometry
                        s = shape(feature['geometry'])
                        area_acres = s.area * (10**4) * 247.105
                        st.session_state.field_total_areas[key] += area_acres  # Accumulate area

            total_area_for_field = st.session_state.field_total_areas.get(key, 0)
            cols[3].write(f"Area: {total_area_for_field:.2f} acres")

            field_data = {
                "geojson": {
                    "type": "Feature",
                    "properties": {},
                    "geometry": value['details']['geometry']
                },
                "color": value['details']['color'],
                "area": f"{total_area_for_field:.2f} acres",
                "STR": value['details'].get('STR', '')
            }
            fields_data.append(field_data)

            value['details'].update({
                "color": color,
                "farm": farm,
                "field_name": field_name,
                "STR": STR
            })

# Track unique colors
unique_colors = set()
for field_details in st.session_state.field_maps.values():
    unique_colors.add(field_details['details']['color'])

st.session_state.unique_colors = unique_colors

# Section for Labels
st.markdown("---")  
st.subheader("Labels")
if st.button("Add Label", key=add_label_key):
    label_key = f'label_{st.session_state.label_id}'
    st.session_state.label_id += 1
    new_map = create_map('marker', label_key)
    st.session_state.marker_maps[label_key] = {'map': new_map, 'details': {'color': '#FFFFFF'}}

# Display each marker map
for key, value in st.session_state.marker_maps.items():
    if key.startswith("label_"):
        with st.expander(f"Label {key.split('_')[1]}"):
            cols = st.columns((1, 3))
            color = cols[0].color_picker("Color", value['details']['color'], key=f"color_marker_{key}")
            label = cols[1].text_input("Label", key=f"label_{key}")
            folium_static(value['map'], width=700, height=450)

st.markdown("---")  
st.subheader("Legend")

# Iterate over unique colors and display legend entries
for color in st.session_state.unique_colors:
    # Display a color box next to the label input
    st.markdown(f"<div style='display: inline-block; margin-right: 10px; vertical-align: middle;'><span style='display: inline-block; width: 25px; height: 25px; background-color: {color}; margin-right: 5px;'></span></div>", unsafe_allow_html=True)
    
    if color not in st.session_state.legend_entries:
        description = st.text_input(f"Label for color {color}", key=f"legend_description_{color}")
        if description:
            st.session_state.legend_entries[color] = description
    else:
        st.text_input(f"Label for color {color}", value=st.session_state.legend_entries[color], key=f"legend_description_{color}")

# Generate JSON
json_data = {
    "report": {
        "title": report_title,
        "grower": grower,
        "printed_on": printed_on.isoformat(),
        "printed_by": printed_by
    },
    "map": {
        "fields": fields_data,
        "markers": [value['details'] for value in st.session_state.marker_maps.values()]
    },
    "legend": {
        "colors": [{"description": st.session_state.legend_entries[color], "color": color} for color in st.session_state.legend_entries]
    }
}

st.markdown("---")  # Divider
st.subheader("Generated JSON")
st.json(json_data)

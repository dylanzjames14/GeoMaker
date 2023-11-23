from streamlit_folium import st_folium
import folium
import streamlit as st
from folium.plugins import Draw
from streamlit_folium import folium_static
from shapely.geometry import shape
from datetime import date
import uuid
from shapely.geometry import MultiPoint

def calculate_centroid(geometry_list):
    """
    Calculate the centroid of a list of geometries (polygons).
    Returns the centroid as a string in 'latitude,longitude' format.
    """
    if not geometry_list:
        return "0,0"  # Default value if list is empty

    centroids = [shape(geometry).centroid for geometry in geometry_list]
    if centroids:
        multi_point = MultiPoint(centroids)
        centroid = multi_point.centroid
        return f"{centroid.y},{centroid.x}"
    return "0,0"

# Function to capture map interaction
def capture_map_interaction(folium_map):
    """
    Captures the interaction with the folium map and returns the centroid and zoom level.
    """
    # Default values
    centroid_lat, centroid_lon = 36.1256, -97.0665
    zoom_level = 11

    # Capture interaction
    centroid_lat, centroid_lon = folium_map.location
    zoom_level = folium_map.zoom_start

    return f"{centroid_lat},{centroid_lon}", zoom_level

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
                value['details']['geometry'] = []  # Initialize the list to store multiple geometries
                for feature in returned_objects['all_drawings']:
                    if feature['geometry']['type'] == 'Polygon':
                        value['details']['geometry'].append(feature['geometry'])  # Store each polygon geometry
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
                "STR": value['details'].get('STR', ''),
                "labelLocation": calculate_centroid(value['details']['geometry'])
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
    st.session_state.marker_maps[label_key] = {'map': new_map, 'details': {'color': '#FFFFFF', 'geometry': None}}

# Display each marker map
for key, value in st.session_state.marker_maps.items():
    if key.startswith("label_"):
        with st.expander(f"Label {key.split('_')[1]}"):
            cols = st.columns((1, 3))
            color = cols[0].color_picker("Color", value['details']['color'], key=f"color_marker_{key}")
            label = cols[1].text_input("Label", key=f"label_{key}")

            # Use st_folium with a unique key for each marker
            returned_objects = st_folium(value['map'], width=700, height=450, key=f"map_marker_{key}")

            # Check for drawings on the map
            if returned_objects is not None:
                if 'all_drawings' in returned_objects and returned_objects['all_drawings']:
                    for feature in returned_objects['all_drawings']:
                        if feature['geometry']['type'] == 'Point':
                            value['details']['geometry'] = feature['geometry']

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

# Section for Map Overview
st.markdown("---")
st.subheader("Report Map")
st.write("Adjust the map to set your map definition in the JSON below.")

# Initial map settings
initial_location = [36.1256, -97.0665]
initial_zoom_level = 11

overview_map = folium.Map(
    location=initial_location,
    zoom_start=initial_zoom_level,
    tiles="https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}",
    attr="Google"
)

# Add fields to the map
for key, field in st.session_state.field_maps.items():
    for geometry in field['details'].get('geometry', []):
        folium.GeoJson(
            geometry,
            name=f"Field {key.split('_')[1]}",
            style_function=lambda x, color=field['details']['color']: {
                'fillColor': color,
                'color': color,
                'weight': 1,
                'fillOpacity': 0.5
            }
        ).add_to(overview_map)

# Add markers to the overview map
for key, marker in st.session_state.marker_maps.items():
    if marker['details'].get('geometry'):
        folium.Marker(
            location=[marker['details']['geometry']['coordinates'][1], marker['details']['geometry']['coordinates'][0]],
            icon=folium.Icon(color=marker['details']['color']),
            popup=folium.Popup(f"{marker['details'].get('label', 'Marker')} ({key.split('_')[1]})")
        ).add_to(overview_map)

# Display the overview map and capture its interaction state
map_state = st_folium(overview_map, width=700, height=500)

# Find centroid marker (assuming the user places a marker for the centroid)
centroid_marker = next((marker for marker in st.session_state.marker_maps.values() 
                        if marker['details'].get('is_centroid')), None)

if centroid_marker and centroid_marker['details'].get('geometry'):
    centroid_location = centroid_marker['details']['geometry']['coordinates']
    map_centroid = f"{centroid_location[1]},{centroid_location[0]}"  # lat, lon
else:
    map_centroid = f"{initial_location[0]},{initial_location[1]}"  # Default to initial location

# Extract zoom level from the map's current state
map_zoom_level = map_state.get("zoom", initial_zoom_level)

# Generate JSON with map definition including the centroid and zoom level
json_data = {
    "report": {
        "title": report_title,
        "grower": grower,
        "printed_on": printed_on.isoformat(),
        "printed_by": printed_by
    },
    "map": {
        "mapDefinition": {
            "centroid": map_centroid,
            "zoomLevel": map_zoom_level
        },
        "fields": fields_data,
        "markers": [value['details'] for value in st.session_state.marker_maps.values()]
    },
    "legend": {
        "colors": [{"description": st.session_state.legend_entries[color], "color": color} for color in st.session_state.legend_entries]
    }
}
# Section for Report JSON
st.markdown("---")
st.subheader("Report JSON")
st.write("Copy the JSON below for your request body in the MapNow Report.")
st.json(json_data)

import folium
import streamlit as st
from folium.plugins import Draw
from streamlit_folium import st_folium
from shapely.geometry import shape, mapping

if not st.session_state.get('initialized'):
    st.session_state.drawn_geometries = []
    st.session_state.drawn_markers = []
    st.session_state.legend_entries = {}
    st.session_state.initialized = True

st.set_page_config(layout="wide")
st.title("MapNow 🗺️")
st.warning("🚧 Work in Progress 🚧")

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
    4. For fields, provide details in the "Grower", "Farm", "Field", "Area", and "STR" inputs.
    5. For markers, provide a label.
    6. To clear all fields and markers and start fresh, click the "Clear all" button.
    """)

location = [36.1256, -97.0665]
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

if returned_objects and 'all_drawings' in returned_objects and returned_objects['all_drawings']:
    for feature in returned_objects['all_drawings']:
        if feature['geometry']['type'] == 'Polygon':
            existing_geometries = [entry['geometry'] for entry in st.session_state.drawn_geometries if 'geometry' in entry]
            if feature['geometry'] not in existing_geometries:
                s = shape(feature['geometry'])
                # Convert the area from square degrees to acres (assuming the map uses EPSG:4326 WGS 84)
                # Note: This is an approximate conversion and might not be accurate for large areas.
                area_acres = s.area * (10**4) * 247.105
                st.session_state.drawn_geometries.append({
                    'geometry': feature['geometry'],
                    'color': '#FFFFFF',
                    'grower': '',
                    'farm': '',
                    'field': '',
                    'area': f"{area_acres:.2f} acres",
                    'STR': ''
                })
        elif feature['geometry']['type'] == 'Point':
            existing_markers = [entry['geometry'] for entry in st.session_state.drawn_markers if 'geometry' in entry]
            if feature['geometry'] not in existing_markers:
                st.session_state.drawn_markers.append({
                    'geometry': feature['geometry'],
                    'color': '#FFFFFF',
                    'label': ''
                })

if st.button("Reset all"):
    st.session_state.drawn_geometries = []
    st.session_state.drawn_markers = []

st.markdown("---")
st.subheader("Report Title")
report_title = st.text_input("", value="Enter your report title here")

st.markdown("---")
st.subheader("Fields")
fields_data = []

for idx, geo_entry in enumerate(st.session_state.drawn_geometries):
    if 'geometry' in geo_entry:
        col1, col2, col3, col4, col5, col6, col7 = st.columns(7)
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
        with col6:
            geo_entry['area'] = st.text_input(f"Area", geo_entry.get('area', '0 acres'), key=f"area_input_{idx}")
        with col7:
            geo_entry['STR'] = st.text_input(f"STR", geo_entry.get('STR', ''), key=f"STR_input_{idx}")

        field_data = {
            "geojson": {
                "type": "Feature",
                "properties": {},
                "geometry": geo_entry['geometry']
            },
            "color": geo_entry['color'],
            "area": geo_entry['area'],
            "STR": geo_entry['STR'],
            "labelLocation": f"{shape(geo_entry['geometry']).centroid.y},{shape(geo_entry['geometry']).centroid.x}"
        }
        fields_data.append(field_data)

st.markdown("---")
st.subheader("Map Labels")

for idx, marker_entry in enumerate(st.session_state.drawn_markers):
    if 'geometry' in marker_entry:
        col1, col2, col3, col4, col5, col6, col7 = st.columns(7)
        with col1:
            st.write(f"Map Label {idx+1}")
        with col2:
            marker_entry['color'] = st.color_picker("Pick a color", marker_entry.get('color', '#000000'), key=f"marker_color_picker_{idx}")
        with col3:
            marker_entry['label'] = st.text_input(f"Label", marker_entry.get('label', ''), key=f"marker_label_input_{idx}")

st.markdown("---")
st.subheader("Legend")

all_colors = set([geo_entry['color'] for geo_entry in st.session_state.drawn_geometries])
all_colors.update([marker_entry['color'] for marker_entry in st.session_state.drawn_markers])

for color in all_colors:
    if color not in st.session_state.legend_entries:
        st.markdown(f"<div style='display: inline-block; margin-right: 10px; vertical-align: middle;'><span style='display: inline-block; width: 25px; height: 25px; background-color: {color}; margin-right: 5px;'></span></div>", unsafe_allow_html=True)
        description = st.text_input(f"Label for color {color}", key=f"legend_description_{color}")
        if description:
            st.session_state.legend_entries[color] = description
    else:
        st.markdown(f"<div style='display: inline-block; margin-right: 10px;'><span style='display: inline-block; width: 25px; height: 25px; background-color: {color}; margin-right: 5px;'></span>{st.session_state.legend_entries[color]}</div>", unsafe_allow_html=True)

st.markdown("---")
st.subheader("Generated JSON")

json_data = {
    "report": {
        "title": report_title
    },
    "map": {
        "mapDefinition": {
            "boundingBox": {
                "topLeft": "40.812776,-74.105974",
                "bottomRight": "40.512776,-73.805974"
            },
            "centroid": f"{location[0]},{location[1]}",
            "zoomLevel": 12
        },
        "fields": fields_data
    },
    "legend": {
        "colors": [{"description": st.session_state.legend_entries[color], "color": color} for color in st.session_state.legend_entries]
    }
}

st.json(json_data)

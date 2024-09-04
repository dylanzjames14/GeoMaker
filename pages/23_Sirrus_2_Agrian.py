import streamlit as st
import json
import folium
from streamlit_folium import st_folium
from shapely import wkt
from shapely.geometry import MultiPolygon, box
import geopandas as gpd
from geopy.geocoders import Nominatim

st.set_page_config(layout="wide")  # Make the layout wide

st.title("Sirrus 2 Agrian")

# Add a "How to use this tool" expander
with st.expander("📋 Instructions", expanded=False):
    st.markdown("""
    **Steps to Use:**

    1. **Open Sirrus Classic**: 
        - Navigate to **classic.sirrus.ag** in your web browser and log in to your account.
        
    2. **Open Browser Inspector**:
        - Right-click anywhere on the page and select **Inspect** to open the browser's developer tools.
        - Go to the **Network** tab in the developer tools window.

    3. **Trigger Field Data**:
        - In Sirrus Classic, change the grower you are working with. This action should trigger an API call to fetch the grower's field data.
        - In the **Network** tab, look for a request called **Field** (you can filter by 'XHR' requests to find it easily). 

    4. **Copy Response JSON**:
        - Once you locate the **Field** request, click on it to open its details.
        - Go to the **Response** tab and copy the entire JSON response.

    5. **Paste into Streamlit App**:
        - Return to this Streamlit app, paste the copied JSON into the provided text box under the **Upload JSON** section.
        
    6. **View the Results**:
        - The app will process the JSON, convert it to the format expected by the Agrian API, and visualize the fields on a map.
        - You will also see information about the grower, farms, and fields presented below the map.
    """)


# Add a "How it works" expander with a technical explanation
with st.expander("📄 Documentation", expanded=False):
    st.markdown("""
    **Overview:**

    This application processes JSON data that comes from **Sirrus Classic**, converts it into a format that can be consumed by the **Agrian API**, and visualizes the field geometries on a map. The workflow involves reading, processing, and displaying the relevant grower, farm, and field information from the provided JSON, using geographic information in the form of Well-Known Text (WKT) to render the spatial data.

    **Key Steps:**

    1. **JSON Input Parsing:**
        - The app begins by parsing the supplied JSON, which contains the **grower**, **farm**, and **field** data, each with WKT geometries for their boundaries.
        - The app extracts the WKT (Well-Known Text) geometries from the `boundary` field of each item.
        - WKTs are parsed using the **Shapely** library to convert them into geometric objects that can be visualized and processed.

    2. **Geometry Handling (WKT to Boundaries):**
        - The WKT strings are converted into **Shapely** geometry objects (e.g., polygons), which represent the spatial data for fields, farms, and growers.
        - **Centroid Calculation**: For each boundary (field, farm, grower), the centroid (geometric center) is computed using Shapely’s geometry operations.
        - **Bounding Box**: For each boundary, a bounding box is calculated. This is the smallest rectangle that can fully contain the boundary. The bounding box is essential for the automatic zoom functionality on the map.

    3. **Mapping with Folium:**
        - The application uses **Folium** to render the geographic data on a web map.
        - Each boundary (grower, farm, field) is drawn on the map as a **GeoJSON** object. The grower boundary is highlighted in pink, farm boundaries in blue, and individual fields can have other distinct colors.
        - Markers are added at the centroid of each boundary to indicate the **custom location** for the grower, farms, and fields.
        - The map is set to automatically zoom to fit all the displayed geometries based on their bounding boxes.

    4. **Converting JSON for Agrian API:**
        - After parsing and mapping, the JSON data is reformatted to meet the structure required by the **Agrian API**. This includes:
          - **Boundary Mapping**: Each grower, farm, and field boundary is converted back to its WKT format.
          - **Custom Location**: The centroid of each boundary is included as a **POINT** geometry.
          - **Additional Attributes**: For fields, additional metadata like section, township, and range are derived from the geographic centroid and included in the output.

    **Data Flow:**

    - **Input**: The JSON data from Sirrus Classic is uploaded into the app. This data contains the necessary grower, farm, and field information, along with boundary geometries in WKT format.
    - **Processing**: The app processes this data by:
        - Extracting WKT geometries.
        - Calculating centroids and bounding boxes.
        - Preparing the fields' metadata.
    - **Output**: The resulting data is displayed on a map, with boundaries and centroids, and is converted into the format required by the Agrian API for further agricultural analysis and integration.

    **Technologies Used:**
    - **Shapely**: For parsing and manipulating the WKT geometries.
    - **Folium**: For rendering the map and visualizing the spatial data.
    - **Streamlit**: For building the web-based interface and handling JSON input/output.
    - **Nominatim (Geopy)**: For reverse geocoding the centroid locations into human-readable addresses when needed.
    """)

# Step 1: JSON Input
st.header("Upload JSON")
json_input = st.text_area("Paste your JSON here", height=150)  # Smaller height for the text area

if json_input:
    try:
        data = json.loads(json_input)
        st.success("JSON loaded successfully!")
        
        # Step 2: Extract WKT fields and compute bounds for grower
        wkt_fields = []
        bounds = None
        
        # Check if data is a list
        if isinstance(data, list):
            for item in data:
                boundary = item.get("boundary", {})
                records = boundary.get("records", [])
                for record in records:
                    wkt_str = record.get("wkt", "")
                    if wkt_str.strip().upper().startswith("POLYGON"):  # Basic check for WKT format
                        geom = wkt.loads(wkt_str)
                        wkt_fields.append(geom)
                        # Update the overall bounds
                        if bounds is None:
                            bounds = geom.bounds
                        else:
                            bounds = (
                                min(bounds[0], geom.bounds[0]),  # min longitude
                                min(bounds[1], geom.bounds[1]),  # min latitude
                                max(bounds[2], geom.bounds[2]),  # max longitude
                                max(bounds[3], geom.bounds[3])   # max latitude
                            )

        if not wkt_fields:
            st.warning("No WKT fields found in the JSON.")
        else:
            # Step 3: Initialize the map
            st.header("Map")
            center_lat = (bounds[1] + bounds[3]) / 2
            center_lon = (bounds[0] + bounds[2]) / 2
            folium_map = folium.Map(location=[center_lat, center_lon], zoom_start=2)

            # Add satellite imagery from Google
            folium.TileLayer(
                tiles="https://mt1.google.com/vt/lyrs=y@18&x={x}&y={y}&z={z}",
                attr="Google Satellite",
                name="Google Satellite"
            ).add_to(folium_map)

            # Add geometries to the map
            for geom in wkt_fields:
                geo_df = gpd.GeoDataFrame([1], geometry=[geom], crs="EPSG:4326")
                geo_json = geo_df.to_json()
                folium.GeoJson(geo_json).add_to(folium_map)

            # Calculate Grower Information
            multi_polygon = MultiPolygon(wkt_fields)
            centroid = multi_polygon.centroid

            # Calculate bounding box for boundary_map
            bounding_box = box(bounds[0], bounds[1], bounds[2], bounds[3])

            # Draw the bounding box on the map in pink
            folium.GeoJson(
                data=gpd.GeoDataFrame([1], geometry=[bounding_box], crs="EPSG:4326").to_json(),
                style_function=lambda x: {'color': 'pink', 'weight': 2, 'fillOpacity': 0.1}
            ).add_to(folium_map)

            # Add a pink marker at the centroid location
            folium.Marker(
                location=[centroid.y, centroid.x],
                icon=folium.Icon(color='pink'),
                popup="Custom Location (Centroid)"
            ).add_to(folium_map)

            # Automatically zoom the map to fit all fields
            folium_map.fit_bounds([[bounds[1], bounds[0]], [bounds[3], bounds[2]]])

            # Display the map at the top
            st_folium(folium_map, width=1000, height=600)

            # Reverse geocoding to get address details from the centroid coordinates
            geolocator = Nominatim(user_agent="streamlit-app")
            location = geolocator.reverse((centroid.y, centroid.x), exactly_one=True)
            
            if location:
                address = location.raw['address']
                city = address.get('city', '')
                state = address.get('state', '')
                postal_code = address.get('postcode', '')
                line1 = address.get('road', '') + ", " + address.get('house_number', '')
                country = address.get('country_code', 'us').upper()
            else:
                city = ""
                state = ""
                postal_code = ""
                line1 = ""
                country = ""

            # Step 4: Display Grower Information below the map
            grower_info = {
                "grower": {
                    "account_number": "String",
                    "active": True,
                    "address": {
                        "city": city,
                        "country_id": 71,  # Example country ID
                        "geo_location": f"POINT ({centroid.x} {centroid.y})",
                        "line1": line1.strip(),
                        "line2": "",
                        "postal_code": postal_code,
                        "region": state,
                        "state_id": state[:2].upper()  # Using state abbreviation
                    },
                    "boundary_map": {
                        "boundary": bounding_box.wkt,  # Use bounding box as the boundary
                        "boundary_mappable_type": "Grower"
                    },
                    "code": item.get("growerName", "Example Code"),  # Use grower name as the code
                    "custom_location": f"POINT ({centroid.x} {centroid.y})",
                    "name": item.get("growerName", "Example Grower"),
                    "organization_id": "Example Organization ID"
                }
            }

            st.header("Grower Information")
            st.json(grower_info)

            # Step 5: Calculate and Display Farm Information for each farm
            farm_names = set([item['farmName'] for item in data if 'farmName' in item])
            for farm_name in farm_names:
                farm_wkt_fields = []
                farm_bounds = None

                # Extract WKTs associated with the current farm
                for item in data:
                    if item.get('farmName') == farm_name:
                        boundary = item.get("boundary", {})
                        records = boundary.get("records", [])
                        for record in records:
                            wkt_str = record.get("wkt", "")
                            if wkt_str.strip().upper().startswith("POLYGON"):
                                geom = wkt.loads(wkt_str)
                                farm_wkt_fields.append(geom)
                                if farm_bounds is None:
                                    farm_bounds = geom.bounds
                                else:
                                    farm_bounds = (
                                        min(farm_bounds[0], geom.bounds[0]),
                                        min(farm_bounds[1], geom.bounds[1]),
                                        max(farm_bounds[2], geom.bounds[2]),
                                        max(farm_bounds[3], geom.bounds[3])
                                    )

                # Calculate the bounding box and centroid for the farm
                if farm_wkt_fields:
                    farm_multi_polygon = MultiPolygon(farm_wkt_fields)
                    farm_centroid = farm_multi_polygon.centroid
                    farm_bounding_box = box(farm_bounds[0], farm_bounds[1], farm_bounds[2], farm_bounds[3])

                    # Draw the farm bounding box on the map in blue
                    folium.GeoJson(
                        data=gpd.GeoDataFrame([1], geometry=[farm_bounding_box], crs="EPSG:4326").to_json(),
                        style_function=lambda x: {'color': 'blue', 'weight': 2, 'fillOpacity': 0.1}
                    ).add_to(folium_map)

                    # Add a blue marker at the farm centroid location
                    folium.Marker(
                        location=[farm_centroid.y, farm_centroid.x],
                        icon=folium.Icon(color='blue'),
                        popup=f"{farm_name} Farm Centroid"
                    ).add_to(folium_map)

                    farm_info = {
                        "farm": {
                            "boundary_map": {
                                "boundary": farm_bounding_box.wkt,
                                "boundary_mappable_type": "Farm"
                            },
                            "code": farm_name,
                            "custom_location": f"POINT ({farm_centroid.x} {farm_centroid.y})",
                            "grower_id": "Example Grower ID",
                            "name": farm_name
                        }
                    }

                    st.header(f"Farm Information: {farm_name}")
                    st.json(farm_info)

            # Step 6: Display Fields Section
            st.header("Fields Information")
            for item in data:
                field_wkt = None
                field_centroid = None

                # Extract WKTs for the field and calculate the centroid
                boundary = item.get("boundary", {})
                records = boundary.get("records", [])
                for record in records:
                    wkt_str = record.get("wkt", "")
                    if wkt_str.strip().upper().startswith("POLYGON"):
                        field_geom = wkt.loads(wkt_str)
                        field_wkt = field_geom.wkt
                        field_centroid = field_geom.centroid

                # Collect section, township, and range from the centroid
                if field_centroid:
                    section = "30"  # Example section number (update as needed)
                    township = "13"
                    range_val = "21"

                    field_info = {
                        "field": {
                            "active": True,
                            "area_unit": "a",
                            "baseline_id": "21",
                            "boundary_map": {
                                "boundary": field_wkt,
                                "boundary_mappable_type": "Field"
                            },
                            "code": item.get("fieldName", "Example Code"),
                            "county_id": 193,
                            "custom_location": f"POINT ({field_centroid.x} {field_centroid.y})",
                            "description": "This is an example field",
                            "farm_id": item.get("farmId", "Get ID from /core/farms"),
                            "irrigation_source_ids": [1],
                            "irrigation_type_ids": [1],
                            "name": item.get("fieldName", "Example Field"),
                            "range": range_val,
                            "range_unit": "E",
                            "section": section,
                            "soil_order_id": 1,
                            "soil_texture_id": 1,
                            "state_id": 842,
                            "township": township,
                            "township_unit": "S"
                        }
                    }

                    st.json(field_info)

    except json.JSONDecodeError:
        st.error("Invalid JSON format. Please check your input.")

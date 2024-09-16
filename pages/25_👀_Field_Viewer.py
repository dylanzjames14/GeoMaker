import streamlit as st
import requests
import pandas as pd

# Import necessary components for embedding HTML
from streamlit.components.v1 import html

st.set_page_config(layout="wide") 

# Step 1: OAuth2 Authentication
def get_access_token(client_id, client_secret, token_url, scope):
    data = {
        "grant_type": "client_credentials",
        "client_id": client_id,
        "client_secret": client_secret,
        "scope": scope
    }
    response = requests.post(token_url, data=data)
    if response.status_code == 200:
        access_token = response.json().get("access_token")
        return access_token
    else:
        st.error(f"Failed to retrieve access token: {response.status_code}")
        return None

# Step 2: Retrieve growers using access token and syncId
def get_growers(access_token, sync_id):
    headers = {"Authorization": f"Bearer {access_token}"}
    grower_url = f"https://sync.agxplatform.com/api/v4/Account/{sync_id}/Grower/All"
    response = requests.get(grower_url, headers=headers)

    if response.status_code == 200:
        growers = response.json()

        if isinstance(growers, list) and len(growers) > 0:
            simplified_growers = [
                {
                    "SyncID": grower.get("SyncID"),
                    "ID": grower.get("ID"),
                    "Name": grower.get("Name"),
                }
                for grower in growers
            ]
            return pd.DataFrame(simplified_growers)
        else:
            st.error("No growers data found.")
            return pd.DataFrame()
    else:
        st.error(f"Failed to retrieve growers: {response.status_code}")
        return pd.DataFrame()

# Step 3: Retrieve basic farms list for a grower
def get_farms(access_token, sync_id, grower_id):
    headers = {"Authorization": f"Bearer {access_token}"}
    farm_url = f"https://sync.agxplatform.com/api/v4/Account/{sync_id}/Grower/{grower_id}/Farm"
    
    response = requests.get(farm_url, headers=headers)

    if response.status_code == 200:
        farms = response.json()

        if isinstance(farms, list) and len(farms) > 0:
            return farms  # Return the raw list of farms for further detailed calls
        else:
            st.error("No farms data found.")
            return []
    else:
        st.error(f"Failed to retrieve farms: {response.status_code}")
        return []

# Step 4: Retrieve detailed information for each farm
def get_farm_details(access_token, sync_id, farm_id):
    headers = {"Authorization": f"Bearer {access_token}"}
    farm_detail_url = f"https://sync.agxplatform.com/api/v4/Account/{sync_id}/Farm/{farm_id}"

    response = requests.get(farm_detail_url, headers=headers)

    if response.status_code == 200:
        farm_detail = response.json()

        farm_info = {
            "SyncID": farm_detail.get("SyncID"),
            "ID": farm_detail.get("ID"),
            "Name": farm_detail.get("Name"),
            "GrowerID": farm_detail.get("GrowerID"),
        }

        return farm_info
    else:
        st.error(f"Failed to retrieve farm details: {response.status_code}")
        return None

# Step 5: Retrieve basic field list for a farm
def get_fields(access_token, sync_id, grower_id, farm_id):
    headers = {"Authorization": f"Bearer {access_token}"}
    field_url = f"https://sync.agxplatform.com/api/v4/Account/{sync_id}/Grower/{grower_id}/Farm/{farm_id}/Field"
    
    response = requests.get(field_url, headers=headers)

    if response.status_code == 200:
        fields = response.json()

        if isinstance(fields, list) and len(fields) > 0:
            return fields
        else:
            st.error("No fields data found.")
            return []
    else:
        st.error(f"Failed to retrieve fields: {response.status_code}")
        return []

# Step 6: Retrieve detailed information for each field
def get_field_details(access_token, sync_id, field_id):
    headers = {"Authorization": f"Bearer {access_token}"}
    field_detail_url = f"https://sync.agxplatform.com/api/v4/Account/{sync_id}/Field/{field_id}"

    response = requests.get(field_detail_url, headers=headers)

    if response.status_code == 200:
        field_detail = response.json()

        # Correctly extract BoundaryWKT and Measure
        boundary_records = field_detail.get("CurrentBoundary", {}).get("Records", [])
        wkt_list = []
        if boundary_records:
            for record in boundary_records:
                wkt_str = record.get("WKT")
                if wkt_str:
                    wkt_list.append(wkt_str)
            measure_data = boundary_records[0].get("Measure", {})
        else:
            measure_data = {}

        measure_value = measure_data.get("Value")
        measure_type = measure_data.get("MeasureType")

        # Convert measure to acres if necessary
        if measure_value is not None:
            if measure_type == "AREA_SQM":  # Square meters
                measure_acres = measure_value * 0.000247105
            elif measure_type == "AREA_SQKM":  # Square kilometers
                measure_acres = measure_value * 247.105
            elif measure_type == "AREA_ACRES":  # Already in acres
                measure_acres = measure_value
            elif measure_type == "AREA_HECTARES":  # Hectares
                measure_acres = measure_value * 2.47105
            else:
                measure_acres = measure_value  # Assume it's in acres if unknown
        else:
            measure_acres = None

        field_info = {
            "SyncID": field_detail.get("SyncID"),
            "ID": field_detail.get("ID"),
            "Name": field_detail.get("Name"),
            "FarmID": field_detail.get("FarmID"),
            "BoundaryWKTs": wkt_list,  # Store list of WKTs
            "Measure": measure_acres,
            "FarmName": field_detail.get("FarmName")  # Ensure FarmName is included
        }

        return field_info
    else:
        st.error(f"Failed to retrieve field details: {response.status_code}")
        return None

# Main function
def main():
    st.title("Field Viewer")
    st.write("This application allows you to view growers, farms, and fields data from the AgX Platform.")

    # Initialize session state variables
    if 'access_token' not in st.session_state:
        st.session_state['access_token'] = None
    if 'growers_df' not in st.session_state:
        st.session_state['growers_df'] = None
    if 'grower_selected' not in st.session_state:
        st.session_state['grower_selected'] = None
    if 'fields_df' not in st.session_state:
        st.session_state['fields_df'] = None

    # Expander for Authorization
    with st.expander("Authorization"):
        token_url = st.text_input("Access Token URL", "https://auth.agxplatform.com/Identity/Connect/Token")
        client_id = st.text_input("Client ID")
        client_secret = st.text_input("Client Secret", type="password")
        scope = st.text_input("Scope", "sync")
        if st.button("Get Access Token"):
            # Step 1: Get Access Token
            access_token = get_access_token(client_id, client_secret, token_url, scope)
            if access_token:
                st.session_state['access_token'] = access_token
                st.success("Access token retrieved successfully!")

    # Only proceed if access token is available
    if st.session_state['access_token']:
        # SyncID input and Fetch button
        sync_id = st.text_input("Sync ID")
        if st.button("Fetch Growers"):
            # Step 2: Get Growers
            st.session_state['growers_df'] = get_growers(st.session_state['access_token'], sync_id)
            if not st.session_state['growers_df'].empty:
                st.success("Growers retrieved successfully!")

        if st.session_state.get('growers_df') is not None and not st.session_state['growers_df'].empty:
            # Dropdown to select a grower by name
            grower_names = st.session_state['growers_df']["Name"].tolist()
            grower_id_map = dict(zip(st.session_state['growers_df']["Name"], st.session_state['growers_df']["ID"]))
            selected_grower = st.selectbox("Select a Grower", grower_names)

            if st.button("Get Fields"):
                grower_id = grower_id_map[selected_grower]
                st.session_state['grower_selected'] = selected_grower
                # Now retrieve farms and fields
                farms = get_farms(st.session_state['access_token'], sync_id, grower_id)
                if farms:
                    detailed_farms = []
                    for farm in farms:
                        farm_id = farm.get("ID")
                        # Retrieve detailed farm information
                        farm_details = get_farm_details(st.session_state['access_token'], sync_id, farm_id)
                        if farm_details:
                            detailed_farms.append(farm_details)

                    if detailed_farms:
                        # Now get fields for each farm
                        detailed_fields = []
                        for farm in detailed_farms:
                            farm_id = farm['ID']
                            farm_name = farm['Name']
                            fields = get_fields(st.session_state['access_token'], sync_id, grower_id, farm_id)
                            if fields:
                                for field in fields:
                                    field_id = field.get("ID")
                                    field_details = get_field_details(st.session_state['access_token'], sync_id, field_id)
                                    if field_details:
                                        # Add the farm name to the field details
                                        field_details['FarmName'] = farm_name
                                        detailed_fields.append(field_details)

                        if detailed_fields:
                            fields_df = pd.DataFrame(detailed_fields)
                            st.session_state['fields_df'] = fields_df
                            st.success("Fields retrieved successfully!")
                else:
                    st.error("No farms found for the selected grower.")

        if st.session_state.get('fields_df') is not None and not st.session_state['fields_df'].empty:
            st.header(f"Fields for Grower: {st.session_state['grower_selected']}")
            # Create a geopandas GeoDataFrame
            import geopandas as gpd
            from shapely import wkt
            from shapely.geometry import mapping
            import folium

            fields_df = st.session_state['fields_df']
            # Explode the 'BoundaryWKTs' column into separate rows
            fields_df = fields_df.explode('BoundaryWKTs').reset_index(drop=True)
            # Rename 'BoundaryWKTs' to 'BoundaryWKT' for clarity
            fields_df = fields_df.rename(columns={'BoundaryWKTs': 'BoundaryWKT'})
            # Drop rows where BoundaryWKT is None
            fields_df = fields_df.dropna(subset=['BoundaryWKT'])

            # Parse the WKT geometries with error handling
            from shapely.errors import WKTReadingError

            def parse_wkt_safe(wkt_str):
                try:
                    geom = wkt.loads(wkt_str)
                    return geom
                except Exception as e:
                    st.error(f"Error parsing WKT: {e}")
                    return None

            fields_df['geometry'] = fields_df['BoundaryWKT'].apply(parse_wkt_safe)
            fields_df = fields_df.dropna(subset=['geometry'])
            
            if not fields_df.empty:
                gdf = gpd.GeoDataFrame(fields_df, geometry='geometry', crs='EPSG:4326')

                # Display the table first
                st.header("Fields Details")
                st.dataframe(gdf[['Name', 'Measure', 'FarmName', 'BoundaryWKT']])

                # Now build the map
                if gdf.geometry.unary_union.is_empty:
                    st.error("No valid geometries to display on the map.")
                else:
                    centroid = gdf.geometry.unary_union.centroid
                    m = folium.Map(location=[centroid.y, centroid.x], zoom_start=12)

                    # Add polygons to the map
                    for idx, row in gdf.iterrows():
                        geom = row['geometry']
                        field_name = row['Name']
                        farm_name = row['FarmName']
                        measure = row['Measure']
                        folium.GeoJson(
                            data=mapping(geom),
                            name=field_name,
                            style_function=lambda x: {
                                'fillColor': 'blue',
                                'color': 'blue',
                                'weight': 1,
                                'fillOpacity': 0.5,
                            },
                            tooltip=folium.Tooltip(f"Name: {field_name}<br>Farm: {farm_name}<br>Measure: {measure}")
                        ).add_to(m)

                    # Extract min and max for x and y from total_bounds
                    minx, miny, maxx, maxy = gdf.total_bounds  # minx = min_longitude, miny = min_latitude

                    # Create bounds in the format [[min_latitude, min_longitude], [max_latitude, max_longitude]]
                    bounds = [[miny, minx], [maxy, maxx]]

                    # Apply fit_bounds with the correct bounds
                    m.fit_bounds(bounds)

                    # Add layer control
                    folium.LayerControl().add_to(m)

                    # Display the map using st.components.v1.html
                    map_html = m._repr_html_()
                    map_height = 600  # Adjust as needed
                    st.header("Field Boundaries Map")
                    html(map_html, width=1000, height=map_height)

            else:
                st.error("No valid field geometries to display.")
        else:
            st.error("No fields data available.")

if __name__ == "__main__":
    main()

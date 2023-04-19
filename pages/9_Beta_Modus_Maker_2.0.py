import streamlit as st
import pandas as pd
import numpy as np
import datetime
import base64

# Create a list of default maximum depths
default_depths = [0, 6, 12, 18, 24, 30, 36]

# Create an empty list to store the maximum depths
max_depths = [0.0]

# Initialize list to store depth references
depth_refs = []

st.title('📋 [Beta] Make Modus Sampling Files')

# Define default checkbox states
default_checkbox_states = {
    "CEC": True,
    "OM": True,
    "pH": True,
    "BpH": True,
    "H_Meq": True,
    "pct H": True,
    "pct K": True,
    "pct Ca": True,
    "pct Mg": True,
    "pct Na": True,
    "Cu": True,
    "K": True,
    "P": True,
    "S": True,
    "Mg": True,
    "Ca": True,
    "B": True,
    "Zn": True,
    "Fe": True,
    "Mn": True,
    "NO3-N": True,
    "Cl": True,
    "Mo": True,
    "Na": True,
    "AC": True,
    "NH4-N": True,
    "OC": True,
    "Si": True,
    "SO4-S": True,
    "BD": False,
    "SS": False,
    "CO3": False,
    "AdjSAR": False,
    "Al": False,
    "BS": False,
    "ECAP": False,
    "EKP": False,
    "EMgP": False,
    "ESP": False,
    "HCO3": False,
    "HM": False,
    "Ni": False,
    "RZM": False,
    "Slake": False,
    "TN": False,
    "TOC": False,
    "K&#58;B": False,
    "K&#58;Mg": False,
    "K&#58;Na": False,
    "Mn&#58;Cu": False,
    "Mn&#58;Zn": False,
    "P&#58;Cu": False,
    "P&#58;Zn": False,
    "P&#58;S": False,
    "P&#58;Mn": False,
    "Zn&#58;Cu": False,
    "CaCO3": False,
}

# Define unique default min/max values for each column
default_min_max_values = {
    "CEC": (10, 40),
    "OM": (1, 6),
    "pH": (5, 8.5),
    "BpH": (5.5, 7.5),
    "H_Meq": (0, 100),
    "pct H": (25,70),
    "pct K": (0, 10),
    "pct Ca": (10, 95),
    "pct Mg": (0.5, 10),
    "pct Na": (0, 5),
    "Cu": (0.2, 10),
    "K": (20, 100),
    "S": (0, 40),
    "Mg": (0, 600),
    "Ca": (50, 400),
    "B": (0.1, 4.0),
    "Zn": (0.2, 10),
    "Fe": (10, 50),
    "Mn": (0, 30),
    "NO3-N": (10, 100),
    "Cl": (0, 50),
    "Mo": (0.1, 0.5),
    "Na": (0, 50),
    "AC": (35, 100),
    "NH4-N": (5, 50),
    "OC": (1, 5),
    "Si": (5, 15),
    "SO4-S": (5, 20),
    "BD": (1, 2),
    "SS": (0.1, 2),
    "CO3": (0.1, 1),
    "AdjSAR": (5, 25),
    "Al": (1, 5),
    "BS": (0, 100),
    "ECAP": (0.5, 5),
    "EKP": (100, 500),
    "EMgP": (50, 400),
    "ESP": (2, 8),
    "HCO3": (0.1, 5),
    "HM": (0, 50),
    "Ni": (5, 30),
    "RZM": (50, 70),
    "Slake": (50, 80),
    "TN": (0.1, 0.5),
    "TOC": (0.3, 3),
    "K&#58;B": (100, 600),
    "K&#58;Mg": (0.1, 3),
    "K&#58;Na": (0, 10),
    "Mn&#58;Cu": (0, 100),
    "Mn&#58;Zn": (20, 100),
    "P&#58;Cu": (0, 10),
    "P&#58;Zn": (0, 10),
    "P&#58;S": (0, 10),
    "P&#58;Mn": (0, 1),
    "Zn&#58;Cu": (0, 6),
    "CaCO3": (1, 2),
    "P": (10, 20),
}

# Define default units for each column
default_units = {
    "CEC": ["meq/100g"],
    "OM": ["%"],
    "pH": ["None"],
    "BpH": ["None"],
    "H_Meq": ["meq/100g"],
    "pct H": ["%"],
    "pct K": ["%", "meq/100g"],
    "pct Ca": ["%", "meq/100g"],
    "pct Mg": ["%", "meq/100g"],
    "pct Na": ["%", "meq/100g"],
    "Cu": ["ppm", "lbs/ac"],
    "K": ["ppm", "lbs/ac"],
    "S": ["ppm", "lbs/ac"],
    "Mg": ["ppm", "lbs/ac"],
    "Ca": ["ppm", "lbs/ac"],
    "B": ["ppm", "lbs/ac"],
    "Zn": ["ppm", "lbs/ac"],
    "Fe": ["ppm", "lbs/ac"],
    "Mn": ["ppm", "lbs/ac"],
    "NO3-N": ["ppm"],
    "Cl": ["ppm"],
    "Mo": ["ppm", "lbs/ac"],
    "Na": ["ppm", "lbs/ac"],
    "AC": ["meq/100g"],
    "NH4-N": ["ppm", "lbs/ac"],
    "OC": ["%"],
    "Si": ["ppm", "lbs/ac"],
    "SO4-S": ["ppm", "lbs/ac"],
    "BD": ["g/cm³"],
    "SS": ["None"],
    "CO3": ["meq/100g"],
    "AdjSAR": ["None"],
    "Al": ["ppm", "lbs/ac"],
    "BS": ["%"],
    "ECAP": ["dS/m"],
    "EKP": ["None"],
    "EMgP": ["None"],
    "ESP": ["%"],
    "HCO3": ["meq/L"],
    "HM": ["%"],
    "Ni": ["ppm", "lbs/ac"],
    "RZM": ["None"],
    "Slake": ["None"],
    "TN": ["%"],
    "TOC": ["%"],
    "K&#58;B": ["None"],
    "K&#58;Mg": ["None"],
    "K&#58;Na": ["None"],
    "Mn&#58;Cu": ["None"],
    "Mn&#58;Zn": ["None"],
    "P&#58;Cu": ["None"],
    "P&#58;Zn": ["None"],
    "P&#58;S": ["None"],
    "P&#58;Mn": ["None"],
    "Zn&#58;Cu": ["None"],
    "CaCO3": ["%"],
    "P": ["ppm", "lbs/ac"],
}

with st.expander("Specify analysis and sample ranges", expanded=False):
    min_sample_id, max_sample_id = st.slider("Set Number Range:", 1, 500, (1, 35))
    
    # Initialize selected_columns dictionary
    selected_columns = {}
    column_units = {}
    
    # Calculate the number of columns needed
    num_columns = 6
    
    # Create the columns
    checkbox_columns = st.columns(num_columns)
    
    # Initialize a counter for the current column
    column_counter = 0

    # Place checkboxes in the columns for each selected column
    for column in default_checkbox_states.keys():
        with checkbox_columns[column_counter].container():
            selected = st.checkbox(column, value=default_checkbox_states.get(column, True))
            selected_columns[column] = selected
            column_counter = (column_counter + 1) % num_columns  # Move to the next column, reset to 0 if num_columns is reached

    # Add a line separator
    st.write("<hr>", unsafe_allow_html=True)

    # Reset the column counter for the next loop
    column_counter = 0

    # Place unit selections in the columns for each selected column
    for column, selected in selected_columns.items():
        if selected:
            with checkbox_columns[column_counter].container():
                default_unit_options = default_units.get(column, ["ppm", "lbs/ac"])
                unit = st.selectbox(f"{column} units", default_unit_options)
                column_units[column] = unit
                column_counter = (column_counter + 1) % num_columns  # Move to the next column, reset to 0 if num_columns is reached

with st.expander("Specify sample depth information", expanded=False):
    # Dropdown to select the number of depths sampled
    depth_unit = st.selectbox("Select Depth Units:", ["in", "cm"])
    num_depths = st.selectbox("Select the # of unique depths for each sample.", [1, 2, 3, 4, 5, 6], key='num_depths', index=0)

    # Input boxes for the maximum depth for topsoil and subsoils
    cols = st.columns(num_depths)
    for i in range(num_depths):
        with cols[i]:
            if i == 0:
                st.write(f'<span style="color: #f67b21">Topsoil</span>', unsafe_allow_html=True)
            else:
                st.write(f'<span style="color: #f67b21">Subsoil {i}</span>', unsafe_allow_html=True)
            if depth_unit == "Inches":
                max_depth = st.number_input(f"Depth ({depth_unit}):", key=f"max_depth_{i}", value=default_depths[i+1])
            else:
                max_depth = st.number_input(f"Depth {i} ({depth_unit}):", key=f"max_depth_{i}", value=default_depths[i+1])
            max_depths.append(max_depth)
            depth_refs.append({
                "DepthID": i+1 if i > 0 else 1,
                "StartingDepth": int(max_depths[i]),
                "EndingDepth": int(max_depth),
                "ColumnDepth": int(max_depth) - int(max_depths[i]),
                "DepthUnit": depth_unit.lower()
            })

# Create DataFrame with specified row range and selected columns, and populate with random values between the specified min/max
data = pd.DataFrame(index=range(min_sample_id, max_sample_id + 1), columns=[col for col, selected in selected_columns.items() if selected])
for column in data.columns:
    min_value, max_value = default_min_max_values[column]
    data[column] = np.random.uniform(min_value, max_value, size=len(data))

# Add the 'SampleNumber' column with values from min_sample_id to max_sample_id
data['SampleNumber'] = range(min_sample_id, max_sample_id + 1)

# Reorder the columns to place 'SampleNumber' as the first column
columns = ['SampleNumber'] + [col for col in data.columns if col != 'SampleNumber']
data = data[columns]

# Display data editor
edited_data = st.experimental_data_editor(data)

# ModusResult metadata
event_date = str(datetime.date.today())
expiration_date = str(datetime.date.today() + datetime.timedelta(days=7))
received_date = str(datetime.date.today())
processed_date = str(datetime.date.today())


# Initialize xml_strings for all samples
xml_strings = ""

value_desc = {
    "CEC": "VL",
    "OM": "VL",
    "pH": "VL",
    "BpH": "VL",
    "H_Meq": "VL",
    "pct H": "VL",
    "pct K": "VL",
    "pct Ca": "VL",
    "pct Mg": "VL",
    "pct Na": "VL",
    "Cu": "VL",
    "P Mehlich III (lbs)": "VL",
    "P Bray I": "VL",
    "K": "VL",
    "S": "VL",
    "Mg": "VL",
    "Ca": "VL",
    "B": "VL",
    "Zn": "VL",
    "Fe": "VL",
    "Mn": "VL",
    "NO3-N": "VL",
    "Cl": "VL",
    "Mo": "VL",
    "Na": "VL",
    "AC": "VL",
    "AdjSAR": "VL",
    "Al": "VL",
    "BD": "VL",
    "BS": "VL",
    "CO3": "VL",
    "ECAP": "VL",
    "EKP": "VL",
    "EMgP": "VL",
    "ESP": "VL",
    "HCO3": "VL",
    "HM": "VL",
    "Mo": "VL",
    "NH4-N": "VL",
    "Ni": "VL",
    "OC": "VL",
    "P BINDX": "VL",
    "RZM": "VL",
    "SAR": "VL",
    "Si": "VL",
    "Slake": "VL",
    "SO4-S": "VL",
    "SS": "VL",
    "TN": "VL",
    "TOC": "VL",
}

# Generate ModusResult metadata
modus_result_metadata = "<ModusResult xmlns:xsi=\"http://www.w3.org/2001/XMLSchema-instance\" Version=\"1.0\" xsi:noNamespaceSchemaLocation=\"modus_result.xsd\">\n"
modus_result_metadata += "<Event>\n"
modus_result_metadata += "<EventMetaData>\n"
modus_result_metadata += "<EventCode>1234-ABCD</EventCode>\n"
modus_result_metadata += f"<EventDate>{event_date}</EventDate>\n"
modus_result_metadata += "<EventType>\n<Soil/>\n</EventType>\n"
modus_result_metadata += f"<EventExpirationDate>{expiration_date}</EventExpirationDate>\n"
modus_result_metadata += "</EventMetaData>\n"
modus_result_metadata += "<LabMetaData>\n"
modus_result_metadata += "<LabName>GeoMaker Analytical</LabName>\n"
modus_result_metadata += "<LabID>1234567</LabID>\n"
modus_result_metadata += "<LabEventID>1234567</LabEventID>\n"
modus_result_metadata += "<TestPackageRefs>\n"
modus_result_metadata += "<TestPackageRef TestPackageID=\"1\">\n"
modus_result_metadata += "<Name>Gold Package</Name>\n"
modus_result_metadata += "<LabBillingCode>1234567</LabBillingCode>\n"
modus_result_metadata += "</TestPackageRef>\n"
modus_result_metadata += "</TestPackageRefs>\n"
modus_result_metadata += f"<ReceivedDate>{received_date}T00:00:00-06:00</ReceivedDate>\n"
modus_result_metadata += f"<ProcessedDate>{processed_date}T00:00:00-06:00</ProcessedDate>\n"
modus_result_metadata += "<Reports>\n"
modus_result_metadata += "<Report>\n"
modus_result_metadata += "<LabReportID>\n"
modus_result_metadata += "</LabReportID>\n"
modus_result_metadata += "<FileDescription>\n"
modus_result_metadata += "</FileDescription>\n"
modus_result_metadata += "<File>\n"
modus_result_metadata += "</File>\n"
modus_result_metadata += "</Report>\n"
modus_result_metadata += "</Reports>\n"
modus_result_metadata += "</LabMetaData>\n"

# Generate XML string for each sample
xml_strings = ""
xml_strings += "<EventSamples>\n"  # Add the EventSamples opening tag
xml_strings += "<Soil>\n"  # Add the Soil opening tag

# Depth references (moved outside the loop)
xml_string = "<DepthRefs>\n"
for depth_ref in depth_refs:
    column_name = f"{depth_ref['StartingDepth']} - {depth_ref['EndingDepth']}"
    xml_string += f"  <DepthRef DepthID=\"{depth_ref['DepthID']}\">\n"
    xml_string += f"    <Name>{column_name}</Name>\n"
    xml_string += f"    <StartingDepth>{depth_ref['StartingDepth']}</StartingDepth>\n"
    xml_string += f"    <EndingDepth>{depth_ref['EndingDepth']}</EndingDepth>\n"
    xml_string += f"    <ColumnDepth>{depth_ref['ColumnDepth']}</ColumnDepth>\n"
    xml_string += f"    <DepthUnit>{depth_ref['DepthUnit']}</DepthUnit>\n"
    xml_string += f"  </DepthRef>\n"
xml_string += "</DepthRefs>\n"
xml_strings += xml_string

for index, row in edited_data.iterrows():
    # Nutrient results for current sample
    xml_string = "<SoilSample>\n"
    xml_string += "<SampleMetaData>\n"
    xml_string += f"  <SampleNumber>{int(row['SampleNumber'])}</SampleNumber>\n"
    xml_string += "<OverwriteResult>false</OverwriteResult>\n"
    xml_string += f"  <Geometry></Geometry>\n"
    xml_string += "</SampleMetaData>\n"
    xml_string += "<Depths>\n"  # Add the Depths opening tag

    for depth_ref in depth_refs:
        xml_string += f"<Depth DepthID=\"{depth_ref['DepthID']}\">\n"  # Add the Depth opening tag
        xml_string += "<NutrientResults>\n"  # Add the NutrientResults opening tag

        for nutrient in edited_data:
            if nutrient not in ['ID', 'SampleNumber'] and selected_columns[nutrient]:
                nutrient_value = row[nutrient]
                nutrient_unit = column_units.get(nutrient, unit.lower())
                nutrient_value_desc = value_desc.get(nutrient, "VL")

                xml_string += f"  <NutrientResult>\n"
                xml_string += f"    <Element>{nutrient}</Element>\n"
                xml_string += f"    <Value>{nutrient_value}</Value>\n"
                xml_string += f"    <ModusTestID>S-{nutrient}-B2-1:7.01.03</ModusTestID>\n"
                xml_string += f"    <ValueType>Measured</ValueType>\n"
                xml_string += f"    <ValueUnit>{nutrient_unit}</ValueUnit>\n"
                xml_string += f"    <ValueDesc>{nutrient_value_desc}</ValueDesc>\n"
                xml_string += f"  </NutrientResult>\n"

        xml_string += "</NutrientResults>\n"  # Add the NutrientResults closing tag
        xml_string += "</Depth>\n"  # Add the Depth closing tag

    xml_string += "</Depths>\n"  # Add the Depths closing tag
    xml_string += "</SoilSample>\n"
    xml_strings += xml_string

xml_strings += "</Soil>\n"  # Add the Soil closing tag
xml_strings += "</EventSamples>\n"  # Add the EventSamples closing tag

# Close the ModusResult tag
xml_strings = modus_result_metadata + xml_strings
xml_strings += "</Event>\n"
xml_strings += "</ModusResult>\n"

# Download button
if xml_strings:
    filename = f"ModusbyGeoMaker.xml"
    b64 = base64.b64encode(xml_strings.encode()).decode()
    href = f'<a href="data:file/xml;base64,{b64}" download="{filename}">Download Modus XML File</a>'
    st.markdown(href, unsafe_allow_html=True)

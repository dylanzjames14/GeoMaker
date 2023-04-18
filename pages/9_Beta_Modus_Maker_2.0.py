import streamlit as st
import pandas as pd
import numpy as np
import datetime
import base64

st.warning("This application is not yet complete. Units are not aligned with Modus or agX standards. Table edits are not retained.")

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
    "K ": True,
    "S ": True,
    "Mg ": True,
    "Ca ": True,
    "B ": True,
    "Zn ": True,
    "Fe ": True,
    "Mn ": True,
    "NO3-N ": True,
    "Cl ": True,
    "Mo ": True,
    "Na ": True,
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
    "Mo": False,
    "Ni": False,
    "RZM": False,
    "Slake": False,
    "TN": False,
    "TOC": False,
}

# Define unique default min/max values for each column
default_min_max_values = {
    "CEC": (0, 100),
    "OM": (0, 100),
    "pH": (0, 100),
    "BpH": (0, 100),
    "H_Meq": (0, 100),
    "pct H": (0, 100),
    "pct K": (0, 100),
    "pct Ca": (0, 100),
    "pct Mg": (0, 100),
    "pct Na": (0, 100),
    "Cu": (0, 100),
    "K ": (0, 100),
    "S ": (0, 100),
    "Mg ": (0, 100),
    "Ca ": (0, 100),
    "B ": (0, 100),
    "Zn ": (0, 100),
    "Fe ": (0, 100),
    "Mn ": (0, 100),
    "NO3-N ": (0, 100),
    "Cl ": (0, 100),
    "Mo ": (0, 100),
    "Na ": (0, 100),
    "AC": (0, 100),
    "NH4-N": (0, 100),
    "OC": (0, 100),
    "Si": (0, 100),
    "SO4-S": (0, 100),
}

# Define default units for each column
default_units = {
    "CEC": ["ppm", "lbs/ac"],
    "OM": ["ppm", "lbs/ac"],
    "pH": ["pH units"],
    "BpH": ["pH units"],
    "H_Meq": ["meq/100g", "meq/L"],
    "pct H": ["%", "g/kg"],
    "pct K": ["%", "g/kg"],
    "pct Ca": ["%", "g/kg"],
    "pct Mg": ["%", "g/kg"],
    "pct Na": ["%", "g/kg"],
    "Cu": ["ppm", "lbs/ac", "mg/kg", "µg/g"],
    "K": ["ppm", "lbs/ac", "mg/kg", "µg/g"],
    "S": ["ppm", "lbs/ac", "mg/kg", "µg/g"],
    "Mg": ["ppm", "lbs/ac", "mg/kg", "µg/g"],
    "Ca": ["ppm", "lbs/ac", "mg/kg", "µg/g"],
    "B": ["ppm", "lbs/ac", "mg/kg", "µg/g"],
    "Zn": ["ppm", "lbs/ac", "mg/kg", "µg/g"],
    "Fe": ["ppm", "lbs/ac", "mg/kg", "µg/g"],
    "Mn": ["ppm", "lbs/ac", "mg/kg", "µg/g"],
    "NO3-N": ["ppm", "lbs/ac", "mg/kg", "µg/g"],
    "Cl": ["ppm", "lbs/ac", "mg/kg", "µg/g"],
    "Mo": ["ppm", "lbs/ac", "mg/kg", "µg/g"],
    "Na": ["ppm", "lbs/ac", "mg/kg", "µg/g"],
    "AC": ["ppm", "lbs/ac", "mg/kg", "µg/g"],
    "NH4-N": ["ppm", "lbs/ac", "mg/kg", "µg/g"],
    "OC": ["ppm", "lbs/ac", "mg/kg", "µg/g"],
    "Si": ["ppm", "lbs/ac", "mg/kg", "µg/g"],
    "SO4-S": ["ppm", "lbs/ac", "mg/kg", "µg/g"],
    "BD": ["g/cm³"],
    "SS": ["kPa"],
    "CO3": ["ppm", "lbs/ac", "mg/kg", "µg/g"],
    "AdjSAR": ["ppm", "mg/L", "meq/L"],
    "Al": ["ppm", "lbs/ac", "mg/kg", "µg/g"],
    "BS": ["%", "g/kg"],
    "ECAP": ["dS/m", "mS/cm", "µS/cm"],
    "EKP": ["dS/m", "mS/cm", "µS/cm"],
    "EMgP": ["dS/m", "mS/cm", "µS/cm"],
    "ESP": ["%", "g/kg"],
    "HCO3": ["ppm", "mg/L", "meq/L"],
    "HM": ["ppm", "mg/L", "meq/L"],
    "Mo": ["ppm", "lbs/ac", "mg/kg", "µg/g"],
    "Ni": ["ppm", "lbs/ac", "mg/kg", "µg/g"],
    "RZM": ["ppm", "lbs/ac", "mg/kg", "µg/g"],
    "Slake": ["%"],
    "TN": ["ppm", "lbs/ac", "mg/kg", "µg/g"],
    "TOC": ["ppm", "lbs/ac", "mg/kg", "µg/g"],
}

with st.expander("Specify analysis and sample ranges", expanded=False):
    min_sample_id, max_sample_id = st.slider("Set Number Range:", 1, 500, (1, 35))
    
    # Initialize selected_columns dictionary
    selected_columns = {}
    column_units = {}
    
    # Calculate the number of columns needed
    num_columns = 5
    
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

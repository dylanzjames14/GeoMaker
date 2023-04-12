import pandas as pd
import streamlit as st
import datetime
import base64

st.set_page_config(layout="wide")
st.title("📋 Make Modus Sampling Results")
st.write("Configure your sampling results file. Your results will be printed below with a download option. Note large results may take awhile to generate.")

# Set default unit as PPM
unit = 'PPM'

# Radio button to select depth units
depth_unit = st.radio("Depth units:", ("Inches", "Centimeters"))

# Load soil test data
soil_test_data = pd.read_excel("Data/ppmSoilTest.xlsx")

# Range sliders for setting min and max range of sample IDs
min_sample_id, max_sample_id = st.slider("Set sample range", 1, 500, (1, 30), 1)

# Filter soil test data based on Sample range
soil_test_data = soil_test_data[(soil_test_data.SampleNumber >= min_sample_id) & (soil_test_data.SampleNumber <= max_sample_id)]

# Create a list of default maximum depths
default_depths = [0, 6, 12, 18, 24, 30, 36]

# Create an empty list to store the maximum depths
max_depths = [0.0]

# Initialize list to store depth references
depth_refs = []

with st.expander("Add subsoils", expanded=False):
    # Dropdown to select the number of depths sampled
    num_depths = st.selectbox("Select the # of unique depths for each sample.", [0, 1, 2, 3, 4, 5], key='num_depths', index=0)

# Input boxes for the maximum depth for topsoil and subsoils
cols = st.columns(num_depths + 1)
for i in range(num_depths + 1):
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

# Display filtered soil test data, hiding columns with missing values
st.write("---")
st.header("Soil Test Results")
st.write("To edit, double-click in a cell and update its value")
filtered_soil_test_data = soil_test_data[(soil_test_data['SampleNumber'] >= min_sample_id) & (soil_test_data['SampleNumber'] <= max_sample_id)]
filtered_soil_test_data = filtered_soil_test_data.drop(columns=['ID'], errors='ignore')  # Drop the 'ID' column if it exists
filtered_soil_test_data = filtered_soil_test_data.dropna(axis=1, how='all')  # Drop columns with all missing values
edited_soil_test_data = st.experimental_data_editor(filtered_soil_test_data)

# Create expander and checkboxes for each header from the .xlxs file
with st.expander("Select analysis to include in the Modus XML file", expanded=False):
    # Calculate the number of columns needed
    num_columns = 6
    # Create the columns
    checkbox_columns = st.columns(num_columns)
    
    # Initialize a counter for the current column
    column_counter = 0

    # Define default checkbox states
default_checkbox_states = {
    "BD": False,
    "SS": False,
    "CO3": False,
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
    "P Mehlich III (lbs)": True,
    "P Bray I ": True,
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
    "AdjSAR": "meq/L",
    "Al": False,
    "BS": False,
    "ECAP": False,
    "EKP": False,
    "EMgP": False,
    "ESP": False,
    "HCO3": False,
    "HM": False,
    "Mo": False,
    "NH4-N": True,
    "Ni": False,
    "OC": True,
    "RZM": False,
    "Si": True,
    "Slake": False,
    "SO4-S": True,
    "TN": False,
    "TOC": False,
}

# Place checkboxes in the columns
selected_columns = {}
for column in filtered_soil_test_data.columns:
    if column != "SampleNumber":
        selected_columns[column] = checkbox_columns[column_counter].checkbox(column, value=default_checkbox_states.get(column, True))
        column_counter = (column_counter + 1) % num_columns  # Move to the next column, reset to 0 if num_columns is reached

# ModusResult metadata
event_date = str(datetime.date.today())
expiration_date = str(datetime.date.today() + datetime.timedelta(days=7))
received_date = str(datetime.date.today())
processed_date = str(datetime.date.today())


# Initialize xml_strings for all samples
xml_strings = ""

value_units = {
    "BD": "grams/mL",
    "SS": "mmhos/cm",
    "CO3": "meq/L",
    "CEC": "meq/100g",
    "OM": "%",
    "pH": "none",
    "BpH": "none",
    "H_Meq": "meq/100g",
    "pct H": "%",
    "pct K": "%",
    "pct Ca": "%",
    "pct Mg": "%",
    "pct Na": "%",
    "Cu": "ppm",
    "P Mehlich III (lbs)": "ppm",
    "P Bray I ": "ppm",
    "K ": "ppm",
    "S ": "ppm",
    "Mg ": "ppm",
    "Ca ": "ppm",
    "B ": "ppm",
    "Zn ": "ppm",
    "Fe ": "ppm",
    "Mn ": "ppm",
    "NO3-N ": "ppm",
    "Cl ": "ppm",
    "Mo ": "ppm",
    "Na ": "ppm",
    "AC": "meq/100 g",
    "AdjSAR": "meq/L",
    "Al": "meq/100g",
    "BS": "%",
    "ECAP": "dS/m",
    "EKP": "ppm",
    "EMgP": "ppm",
    "ESP": "none",
    "HCO3": "meq/L",
    "HM": "%",
    "Mo": "ppm",
    "NH4-N": "ppm",
    "Ni": "ppm",
    "OC": "%",
    "RZM": "%",
    "Si": "ppm",
    "Slake": "%",
    "SO4-S": "ppm",
    "TN": "%",
    "TOC": "%",
}

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

for index, row in edited_soil_test_data.iterrows():
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

        for nutrient in filtered_soil_test_data.columns:
            if nutrient not in ['ID', 'SampleNumber'] and selected_columns[nutrient]:
                nutrient_value = row[nutrient]
                nutrient_unit = value_units.get(nutrient, unit.lower())
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

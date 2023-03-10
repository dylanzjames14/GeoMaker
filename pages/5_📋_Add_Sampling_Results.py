import pandas as pd
import streamlit as st
import datetime
import base64

st.info("This app is under construction.")
st.title("Generate Modus Sampling Results")

# Create 3 columns to hold the radio buttons for selecting the analysis and depth units
col1, col2 = st.columns(2)

# Radio button to select between LBS and PPM
with col1:
    unit = st.radio("Analysis units:", ('LBS', 'PPM'))

# Radio button to select depth units
with col2:
    depth_unit = st.radio("Depth units:", ("Inches", "Centimeters"))

# Load soil test data
if unit == 'LBS':
    soil_test_data = pd.read_excel("Data/lbsSoilTest.xlsx")
else:
    soil_test_data = pd.read_excel("Data/ppmSoilTest.xlsx")

# Range sliders for setting min and max range of sample IDs
min_sample_id, max_sample_id = st.slider("Set sample range", 1, 500, (1, 30), 1)

# Filter soil test data based on Sample range
soil_test_data = soil_test_data[(soil_test_data.SampleNumber >= min_sample_id) & (soil_test_data.SampleNumber <= max_sample_id)]

# Dropdown to select the number of depths sampled
num_depths = st.selectbox("Unique depths collected at each sample", [0, 1, 2, 3, 4, 5], key='num_depths', index=0)

# Create a list of default maximum depths
default_depths = [0, 6, 12, 18, 24, 30, 36]

# Create an empty list to store the maximum depths
max_depths = [0.0]

# Initialize list to store depth references
depth_refs = []

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
            "StartingDepth": max_depths[i],
            "EndingDepth": max_depth,
            "ColumnDepth": max_depth - max_depths[i],
            "DepthUnit": depth_unit.lower()
        })


# Display filtered soil test data, hiding columns with missing values
st.write("---")
st.write("Soil Test Data")
filtered_soil_test_data = soil_test_data[(soil_test_data['SampleNumber'] >= min_sample_id) & (soil_test_data['SampleNumber'] <= max_sample_id)]
filtered_soil_test_data = filtered_soil_test_data.drop(columns=['ID'], errors='ignore')  # Drop the 'ID' column if it exists
filtered_soil_test_data = filtered_soil_test_data.dropna(axis=1, how='all')  # Drop columns with all missing values
st.experimental_data_editor(filtered_soil_test_data)

# Display depth references and corresponding XML strings for all samples
st.write("---")
st.write("Depth References and XML Strings")

# ModusResult metadata
event_date = str(datetime.date.today())
expiration_date = str(datetime.date.today() + datetime.timedelta(days=7))
received_date = str(datetime.date.today())
processed_date = str(datetime.date.today())

# Initialize xml_strings for all samples
xml_strings = ""

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
modus_result_metadata += "<TestPackageRefs>\n"
modus_result_metadata += "<TestPackageRef TestPackageID=\"1\">\n"
modus_result_metadata += "<Name>Gold Package</Name>\n"
modus_result_metadata += "<LabBillingCode>1234567</LabBillingCode>\n"
modus_result_metadata += "</TestPackageRef>\n"
modus_result_metadata += "</TestPackageRefs>\n"
modus_result_metadata += f"<ReceivedDate>{received_date}T00:00:00-06:00</ReceivedDate>\n"
modus_result_metadata += f"<ProcessedDate>{processed_date}T00:00:00-06:00</ProcessedDate>\n"
modus_result_metadata += "<Reports></Reports>\n"
modus_result_metadata += "</LabMetaData>\n"
modus_result_metadata += "</Event>\n"
modus_result_metadata += "</ModusResult>\n"

# Add ModusResult metadata to xml_strings
xml_strings += modus_result_metadata

# Iterate over rows in filtered_soil_test_data
for index, row in filtered_soil_test_data.iterrows():
    # Sample metadata
    sample_id = row['SampleNumber']

    # Generate XML string for current sample
    xml_string = "<Sample>\n"
    xml_string += f"  <SampleNumber>{sample_id}</SampleNumber>\n"
    xml_string += f"  <ValueUnit>{unit}</ValueUnit>\n"

    # Depth references for current sample
    for depth_ref in depth_refs:
        column_name = f"{depth_ref['StartingDepth']} - {depth_ref['EndingDepth']}"
        xml_string += f"  <DepthRef DepthID=\"{depth_ref['DepthID']}\">\n"
        xml_string += f"  </DepthRef>\n"
    
    # Nutrient results for current sample
    for nutrient in soil_test_data.columns:
        if nutrient not in ['ID', 'SampleNumber']:
            nutrient_value = row[nutrient]
            nutrient_unit = unit.lower() if unit == 'PPM' else 'lbs/acre'
            xml_string += f" <Element>{nutrient}</Element>\n"
            xml_string += f" <Value>{nutrient_value}</Value>\n"
            xml_string += f" <ModusTestID>S-{nutrient}-1:1.02.07</ModusTestID>\n"
            # Set the value unit for each element
value_units = {
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
    "P Mehlich III (lbs)": "lbs/acre",
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
    "Na ": "ppm"
}

# Iterate over rows in filtered_soil_test_data
for index, row in filtered_soil_test_data.iterrows():
    # Sample metadata
    sample_id = row['SampleNumber']

    # Generate XML string for current sample
    xml_string = "<Sample>\n"
    xml_string += f"  <SampleNumber>{sample_id}</SampleNumber>\n"
    xml_string += f"  <ValueUnit>{unit}</ValueUnit>\n"

    # Depth references for current sample
    for depth_ref in depth_refs:
        column_name = f"{depth_ref['StartingDepth']} - {depth_ref['EndingDepth']}"
        xml_string += f"  <DepthRef DepthID=\"{depth_ref['DepthID']}\">\n"
        xml_string += f"  </DepthRef>\n"

    # Nutrient results for current sample
    for nutrient in soil_test_data.columns:
        if nutrient not in ['ID', 'SampleNumber']:
            nutrient_value = row[nutrient]
            nutrient_unit = value_units.get(nutrient, unit.lower())

            xml_string += f"  <NutrientResult>\n"
            xml_string += f"    <Element>{nutrient}</Element>\n"
            xml_string += f"    <Value>{nutrient_value}</Value>\n"
            xml_string += f"    <ModusTestID>S-{nutrient}-1:1.02.07</ModusTestID>\n"
            xml_string += f"    <ValueType>Measured</ValueType>\n"
            xml_string += f"    <ValueUnit>{nutrient_unit}</ValueUnit>\n"
            xml_string += f"  </NutrientResult>\n"

    xml_string += "</Sample>\n"
    xml_strings += xml_string

print(xml_strings)

# Download button
if xml_strings:
    filename = f"GeoMakerModus.xml"
    b64 = base64.b64encode(xml_strings.encode()).decode()
    href = f'<a href="data:file/xml;base64,{b64}" download="{filename}">Download {filename}</a>'
    st.markdown(href, unsafe_allow_html=True)

# Display the XML strings
st.code(xml_strings, language='xml')

import streamlit as st
import pandas as pd
import numpy as np
import datetime
import base64
from lxml import etree
from io import BytesIO
import os

# Set page configuration
st.set_page_config(page_title="Geomaker", page_icon="🌍", layout="wide")
st.title("📋 Make Mock Sampling Results")
st.write("Configure your sampling results file using the options in the expander menus.")

# Initialize default variables
default_depths = [0, 6, 12, 18, 24, 30, 36]
default_checkbox_states = {
    "pH": True,
    "BpH": True,
    "AC": True,
    "OM": True,
    "OC": True,
    "NO3-N": True,
    "NH4-N": True,
    "P(B1)": True,
    "P(B2)": False,
    "P(Cald)": False,
    "P(Olsen)": False,
    "P(M1)": False,
    "P(M2)": False,
    "K": True,
    "Ca": True,
    "Mg": True,
    "S": True,
    "SO4-S": True,
    "Fe": True,
    "Mn": True,
    "Zn": True,
    "Cu": True,
    "B": True,
    "Mo": True,
    "Cl": True,
    "Na": True,
    "CEC": True,
    "Si": True,
    "H_Meq": True,
    "pct H": True,
    "pct K": True,
    "pct Ca": True,
    "pct Mg": True,
    "pct Na": True,
    "BD": False,
    "SS": False,
    "CO3": False,
    "AdjSAR": False,
    "SAR": False,
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
    "K:B": False,
    "K:Mg": False,
    "K:Na": False,
    "Mn:Cu": False,
    "Mn:Zn": False,
    "P:Cu": False,
    "P:Zn": False,
    "P:S": False,
    "P:Mn": False,
    "Zn:Cu": False,
    "CaCO3": False,
    "ENR": False,
    "EC": False,
    "Humic Matter": False,
}

# Define unique default ModusTestID values for each column
default_modus_test_ids = {
    "P(B1)": "S-P-B1-1:10.01.03",
    "P(B2)": "S-P-B2-1:10.01.03",
    "P(Cald)": "S-P-CALD.01.03",
    "P(Olsen)": "S-P-BIC.01.03",
    "P(M1)": "S-P-M1.04",
    "P(M2)": "S-P-M2.04",
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
    "SAR": (5, 25),
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
    "ENR": (1,100),
    "EC": (.2,2),
    "P(B1)": (1,60),
    "P(B2)": (1,60),
    "P(Cald)": (1,60),
    "P(Olsen)": (1,60),
    "P(M1)": (1,60),
    "P(M2)": (1,60),
    "Humic Matter": (0,5),
}

default_decimal_precisions = {
    "CEC": 1,
    "OM": 1,
    "pH": 2,
    "BpH": 2,
    "H_Meq": 1,
    "pct H": 1,
    "pct K": 1,
    "pct Ca": 1,
    "pct Mg": 1,
    "pct Na": 1,
    "Cu": 1,
    "K": 0,
    "S": 0,
    "Mg": 1,
    "Ca": 0,
    "B": 1,
    "Zn": 1,
    "Fe": 0,
    "Mn": 1,
    "NO3-N": 1,
    "Cl": 0,
    "Mo": 1,
    "Na": 1,
    "AC": 1,
    "NH4-N": 1,
    "OC": 1,
    "Si": 1,
    "SO4-S": 1,
    "BD": 1,
    "SS": 1,
    "CO3": 1,
    "AdjSAR": 1,
    "SAR": 1,
    "Al": 1,
    "BS": 1,
    "ECAP": 1,
    "EKP": 1,
    "EMgP": 1,
    "ESP": 1,
    "HCO3": 1,
    "HM": 1,
    "Ni": 1,
    "RZM": 1,
    "Slake": 1,
    "TN": 1,
    "TOC": 1,
    "K&#58;B": 1,
    "K&#58;Mg": 1,
    "K&#58;Na": 1,
    "Mn&#58;Cu": 1,
    "Mn&#58;Zn": 1,
    "P&#58;Cu": 1,
    "P&#58;Zn": 1,
    "P&#58;S": 1,
    "P&#58;Mn": 1,
    "Zn&#58;Cu": 1,
    "CaCO3": 0,
    "ENR": 0,
    "EC": 1,
    "P(B1)": 0,
    "P(B2)": 0,
    "P(Cald)": 0,
    "P(Olsen)": 0,
    "P(M1)": 0,
    "P(M2)": 0,
    "Humic Matter": 0,
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
    "BD": ["g/cm3","grams/20cm3","grams/mL"],
    "SS": ["mmhos/cm"],
    "CO3": ["meq/L"],
    "AdjSAR": ["None"],
    "SAR": ["None"],
    "Al": ["ppm", "lbs/ac"],
    "BS": ["%"],
    "ECAP": ["dS/m"],
    "EKP": ["None"],
    "EMgP": ["None"],
    "ESP": ["%"],
    "HCO3": ["meq/L"],
    "HM": ["%"],
    "Ni": ["ppm", "lbs/ac"],
    "RZM": ["mm","in","cm"],
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
    "ENR": ["lbs/ac"],
    "EC": ["mmhos/cm"],
    "P(B1)": ["ppm", "lbs/ac"],
    "P(B2)": ["ppm", "lbs/ac"],
    "P(Cald)": ["ppm", "lbs/ac"],
    "P(Olsen)": ["ppm", "lbs/ac"],
    "P(M1)": ["ppm", "lbs/ac"],
    "P(M2)": ["ppm", "lbs/ac"],
    "Humic Matter": ["%"],
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
    "Humic Matter": "VL",
}

# Initialize session state variables
if 'selected_columns' not in st.session_state:
    st.session_state.selected_columns = default_checkbox_states.copy()
if 'data' not in st.session_state:
    st.session_state.data = None
if 'min_sample_id' not in st.session_state:
    st.session_state.min_sample_id = None
if 'max_sample_id' not in st.session_state:
    st.session_state.max_sample_id = None
if 'column_units' not in st.session_state:
    st.session_state.column_units = {}

# Expander for analysis and sample ranges
with st.expander("Specify analysis and sample ranges", expanded=False):
    min_sample_id, max_sample_id = st.slider("Set Number Range:", 1, 500, (1, 35))

    # Buttons for selecting/deselecting all checkboxes
    col_select_all, col_deselect_all = st.columns(2)
    with col_select_all:
        select_all = st.button('Select All')
    with col_deselect_all:
        deselect_all = st.button('Deselect All')

    # Initialize temporary variable to store checkbox states
    checkbox_states = {}

    # Display checkboxes and unit selectors
    num_columns = 6
    checkbox_columns = st.columns(num_columns)
    for idx, (column, default_value) in enumerate(default_checkbox_states.items()):
        col = checkbox_columns[idx % num_columns]
        with col:
            # Use a unique key for each checkbox
            checkbox_key = f"checkbox_{column}"
            # Determine the checkbox value
            if select_all:
                checkbox_value = True
            elif deselect_all:
                checkbox_value = False
            else:
                checkbox_value = st.session_state.selected_columns.get(column, default_value)
            # Display the checkbox
            checkbox_states[column] = st.checkbox(column, value=checkbox_value, key=checkbox_key)
            # If checkbox is selected, show unit selection
            if checkbox_states[column]:
                unit_options = default_units.get(column, ["ppm", "lbs/ac"])
                selected_unit = st.selectbox(f"{column} units", unit_options, key=f"unit_{column}")
                st.session_state.column_units[column] = selected_unit

    # Update session state with the new checkbox states
    st.session_state.selected_columns = checkbox_states.copy()

# Expander for sample depth information
with st.expander("Specify sample depth information", expanded=False):
    # Reset depth-related variables
    max_depths = [0.0]
    depth_refs = []

    # Depth units
    depth_unit = st.selectbox("Select Depth Units:", ["Inches", "Centimeters"])
    num_depths = st.selectbox("Select the # of unique depths for each sample.", [1, 2, 3, 4, 5, 6], index=0)

    # Input for depths
    cols = st.columns(num_depths)
    for i in range(num_depths):
        with cols[i]:
            depth_label = "Topsoil" if i == 0 else f"Subsoil {i}"
            st.write(f'<span style="color: #f67b21">{depth_label}</span>', unsafe_allow_html=True)
            max_depth = st.number_input(f"Depth ({depth_unit}):", key=f"max_depth_{i}", value=default_depths[i+1])
            max_depths.append(max_depth)
            depth_refs.append({
                "DepthID": i + 1,
                "StartingDepth": int(max_depths[i]),
                "EndingDepth": int(max_depth),
                "ColumnDepth": int(max_depth) - int(max_depths[i]),
                "DepthUnit": depth_unit.lower()
            })

# Function to create data frame
def create_data_frame():
    selected_columns = st.session_state.selected_columns
    columns = ['SampleNumber'] + [col for col, selected in selected_columns.items() if selected]
    data = pd.DataFrame(index=range(min_sample_id, max_sample_id + 1), columns=columns)
    data['SampleNumber'] = range(min_sample_id, max_sample_id + 1)
    return data

# Check if we need to create or update the data frame
def should_create_new_data():
    if st.session_state.data is None:
        return True
    if min_sample_id != st.session_state.min_sample_id or max_sample_id != st.session_state.max_sample_id:
        return True
    if st.session_state.selected_columns != st.session_state.get('prev_selected_columns', {}):
        return True
    return False

# Create or update data frame
if should_create_new_data():
    st.session_state.data = create_data_frame()
    st.session_state.min_sample_id = min_sample_id
    st.session_state.max_sample_id = max_sample_id
    st.session_state.prev_selected_columns = st.session_state.selected_columns.copy()

# Generate random values
if st.button("Generate Random Values"):
    data = st.session_state.data
    for column in data.columns:
        if column != 'SampleNumber':
            min_value, max_value = default_min_max_values.get(column, (0, 100))
            decimal_precision = default_decimal_precisions.get(column, 2)
            random_values = np.random.uniform(min_value, max_value, size=len(data))
            rounded_values = np.round(random_values, decimal_precision)
            data[column] = rounded_values
    st.session_state.data = data

# Display data editor
edited_data = st.data_editor(st.session_state.data)
st.session_state.data = edited_data

# ModusResult metadata
event_date = str(datetime.date.today())
expiration_date = str(datetime.date.today() + datetime.timedelta(days=7))
received_date = str(datetime.date.today())
processed_date = str(datetime.date.today())

# Generate XML content
def generate_modus_xml(data, depth_refs):
    xml_strings = ""
    xml_strings += "<EventSamples>\n<Soil>\n"
    # Depth references
    xml_strings += "<DepthRefs>\n"
    for depth_ref in depth_refs:
        column_name = f"{depth_ref['StartingDepth']} - {depth_ref['EndingDepth']}"
        xml_strings += f"  <DepthRef DepthID=\"{depth_ref['DepthID']}\">\n"
        xml_strings += f"    <Name>{column_name}</Name>\n"
        xml_strings += f"    <StartingDepth>{depth_ref['StartingDepth']}</StartingDepth>\n"
        xml_strings += f"    <EndingDepth>{depth_ref['EndingDepth']}</EndingDepth>\n"
        xml_strings += f"    <ColumnDepth>{depth_ref['ColumnDepth']}</ColumnDepth>\n"
        xml_strings += f"    <DepthUnit>{depth_ref['DepthUnit']}</DepthUnit>\n"
        xml_strings += f"  </DepthRef>\n"
    xml_strings += "</DepthRefs>\n"
    # Samples
    for index, row in data.iterrows():
        xml_strings += "<SoilSample>\n<SampleMetaData>\n"
        xml_strings += f"  <SampleNumber>{int(row['SampleNumber'])}</SampleNumber>\n"
        xml_strings += "  <OverwriteResult>false</OverwriteResult>\n"
        xml_strings += "  <Geometry></Geometry>\n"
        xml_strings += "</SampleMetaData>\n<Depths>\n"
        for depth_ref in depth_refs:
            xml_strings += f"<Depth DepthID=\"{depth_ref['DepthID']}\">\n<NutrientResults>\n"
            for nutrient in data.columns:
                if nutrient not in ['ID', 'SampleNumber'] and st.session_state.selected_columns.get(nutrient, False):
                    nutrient_value = row[nutrient]
                    nutrient_unit = st.session_state.column_units.get(nutrient, 'none')
                    nutrient_value_desc = value_desc.get(nutrient, "VL")
                    modus_test_id = default_modus_test_ids.get(nutrient, f"S-{nutrient}-B2-1:7.01.03")
                    decimal_precision = default_decimal_precisions.get(nutrient, 2)
                    rounded_nutrient_value = format(round(nutrient_value, decimal_precision), f".{decimal_precision}f")
                    xml_strings += f"  <NutrientResult>\n"
                    xml_strings += f"    <Element>{nutrient}</Element>\n"
                    xml_strings += f"    <Value>{rounded_nutrient_value}</Value>\n"
                    xml_strings += f"    <ModusTestID>{modus_test_id}</ModusTestID>\n"
                    xml_strings += f"    <ValueType>Measured</ValueType>\n"
                    xml_strings += f"    <ValueUnit>{nutrient_unit}</ValueUnit>\n"
                    xml_strings += f"    <ValueDesc>{nutrient_value_desc}</ValueDesc>\n"
                    xml_strings += f"  </NutrientResult>\n"
            xml_strings += "</NutrientResults>\n</Depth>\n"
        xml_strings += "</Depths>\n</SoilSample>\n"
    xml_strings += "</Soil>\n</EventSamples>\n"
    return xml_strings

# Generate XML metadata
modus_result_metadata = f"""<ModusResult xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" Version="1.0" xsi:noNamespaceSchemaLocation="modus_result.xsd">
<Event>
<EventMetaData>
<EventCode>1234-ABCD</EventCode>
<EventDate>{event_date}</EventDate>
<EventType><Soil/></EventType>
<EventExpirationDate>{expiration_date}</EventExpirationDate>
</EventMetaData>
<LabMetaData>
<LabName>GeoMaker Analytical</LabName>
<LabID>1234567</LabID>
<LabEventID>1234567</LabEventID>
<TestPackageRefs>
<TestPackageRef TestPackageID="1">
<Name>Gold Package</Name>
<LabBillingCode>1234567</LabBillingCode>
</TestPackageRef>
</TestPackageRefs>
<ReceivedDate>{received_date}T00:00:00-06:00</ReceivedDate>
<ProcessedDate>{processed_date}T00:00:00-06:00</ProcessedDate>
<Reports>
<Report>
<LabReportID></LabReportID>
<FileDescription></FileDescription>
<File></File>
</Report>
</Reports>
</LabMetaData>
"""

# Generate full XML content
xml_content = modus_result_metadata + generate_modus_xml(st.session_state.data, depth_refs) + "</Event>\n</ModusResult>\n"

# Download button
filename = "ModusbyGeoMaker.xml"
st.download_button(
    label="Download Modus XML File",
    data=xml_content,
    file_name=filename,
    mime='application/xml'
)

# XML Validator Expander
with st.expander("✅ Modus file validator", expanded=False):
    class SchemaEntityResolver(etree.Resolver):
        def resolve(self, url, pubid, context):
            if 'modus_global.xsd' in url:
                return self.resolve_filename(os.path.join('Data', 'modus_global.xsd'), context)
            elif 'modus_submit.xsd' in url:
                return self.resolve_filename(os.path.join('Data', 'modus_submit.xsd'), context)
            return self.resolve_filename(url, context)

    def validate_xml(xml_data, schema_path):
        try:
            parser = etree.XMLParser(load_dtd=True, no_network=False)
            parser.resolvers.add(SchemaEntityResolver())
            schema_doc = etree.parse(schema_path, parser)
            schema = etree.XMLSchema(schema_doc)

            xml_parser = etree.XMLParser(schema=schema)
            etree.parse(BytesIO(xml_data.encode('utf-8')), xml_parser)
            return True, None
        except etree.XMLSchemaError as e:
            return False, str(e)
        except etree.XMLSyntaxError as e:
            return False, str(e)

    # Upload the XML file
    uploaded_file = st.file_uploader("Upload your file to see if it's a valid Modus file.", type="xml")
    if uploaded_file is not None:
        xml_data = uploaded_file.read().decode('utf-8')

        # Set the schema file path
        schema_path = os.path.join("Data", "modus_result.xsd")

        is_valid, error_message = validate_xml(xml_data, schema_path)

        if is_valid:
            st.success("The XML file is valid.")
        else:
            st.error(f"Invalid XML file. Error message: {error_message}")

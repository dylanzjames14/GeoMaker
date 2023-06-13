import streamlit as st
import pandas as pd
import numpy as np
import datetime
import base64
from lxml import etree
from io import StringIO, BytesIO
import os

st.set_page_config(layout="wide")
st.title("📋 Make Modus Sampling Results")
st.write("Configure your sampling results file using the options in the expander menus.")

# Create a list of default maximum depths
default_depths = [0, 6, 12, 18, 24, 30, 36]

# Create an empty list to store the maximum depths
max_depths = [0.0]

# Initialize list to store depth references
depth_refs = []

# Define default checkbox states
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
    "ENR": False,
    "EC": False,
    "Moisture": False,
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
    "Moisture": (1,20),
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
    "Moisture": 1,
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
    "BD": ["g/cm³"],
    "SS": ["None"],
    "CO3": ["meq/100g"],
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
    "ENR": ["lbs/ac"],
    "EC": ["mmhos/cm"],
    "Moisture": ["%"],
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

with st.expander("Specify analysis and sample ranges", expanded=False):
    min_sample_id, max_sample_id = st.slider("Set Number Range:", 1, 500, (1, 35))
    
    # Create two columns for the buttons
    button_columns = st.columns(15)

    # Add buttons for selecting/deselecting all checkboxes
    with button_columns[0]:
        select_all = st.button('Select All')
    with button_columns[1]:
        deselect_all = st.button('Deselect All')

    # Update default_checkbox_states based on button clicks
    if select_all:
        for column in default_checkbox_states.keys():
            default_checkbox_states[column] = True
            st.session_state[column] = True  # Save to session state
    elif deselect_all:
        for column in default_checkbox_states.keys():
            default_checkbox_states[column] = False
            st.session_state[column] = False  # Save to session state
    
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
            if column not in st.session_state:  # Initialize session state for checkbox
                st.session_state[column] = default_checkbox_states.get(column, True)
            selected = st.checkbox(column, value=st.session_state[column])
            selected_columns[column] = selected
            column_counter = (column_counter + 1) % num_columns  # Move to the next column, reset to 0 if num_columns is reached

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

# Check if the data already exists in the st.session_state, otherwise create and populate a new DataFrame
if 'data' not in st.session_state:
    data = pd.DataFrame(index=range(min_sample_id, max_sample_id + 1), columns=[col for col, selected in selected_columns.items() if selected])
    st.session_state.data = data
else:
    data = st.session_state.data


# Add a button to generate random values
if st.button("Generate Random Values"):
    for column in data.columns:
        if column != 'SampleNumber':  # Skip the 'SampleNumber' column
            min_value, max_value = default_min_max_values[column]
            decimal_precision = default_decimal_precisions.get(column, 2)  # Default to 2 decimal places if not specified
            random_values = np.random.uniform(min_value, max_value, size=len(data))
            rounded_values = np.round(random_values, decimal_precision)
            st.session_state.data[column] = rounded_values

# Add the 'SampleNumber' column with values from min_sample_id to max_sample_id
if ('data' not in st.session_state
    or min_sample_id != st.session_state.get('min_sample_id', None)
    or max_sample_id != st.session_state.get('max_sample_id', None)
    or any(selected_columns[col] != st.session_state.selected_columns.get(col, None) for col in selected_columns.keys())):
    data = pd.DataFrame(index=range(min_sample_id, max_sample_id + 1), columns=[col for col, selected in selected_columns.items() if selected])
    data['SampleNumber'] = range(min_sample_id, max_sample_id + 1)

    # Reorder the columns to place 'SampleNumber' as the first column
    columns = ['SampleNumber'] + [col for col in data.columns if col != 'SampleNumber']
    data = data[columns]

    # Save the DataFrame to the session state
    st.session_state.data = data

    # Save the min_sample_id and max_sample_id to the session state
    st.session_state.min_sample_id = min_sample_id
    st.session_state.max_sample_id = max_sample_id

    # Save the selected_columns to the session state
    st.session_state.selected_columns = selected_columns
else:
    data = st.session_state.data

# Display data editor
edited_data = st.experimental_data_editor(st.session_state.data)

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
            if nutrient not in ['ID', 'SampleNumber'] and nutrient in selected_columns and selected_columns[nutrient]:
                nutrient_value = row[nutrient]
                nutrient_unit = column_units.get(nutrient, unit.lower())
                nutrient_value_desc = value_desc.get(nutrient, "VL")

                # Use default ModusTestID value if available, otherwise use the current value
                modus_test_id = default_modus_test_ids.get(nutrient, f"S-{nutrient}-B2-1:7.01.03")

                # Round the nutrient value using the specified decimal precision
                decimal_precision = default_decimal_precisions.get(nutrient, 2)  # Default to 2 decimal places if not specified
                rounded_nutrient_value = format(round(nutrient_value, decimal_precision), f".{decimal_precision}f")

                xml_string += f"  <NutrientResult>\n"
                xml_string += f"    <Element>{nutrient}</Element>\n"
                xml_string += f"    <Value>{rounded_nutrient_value}</Value>\n"
                xml_string += f"    <ModusTestID>{modus_test_id}</ModusTestID>\n"
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

# Create the expander
xml_validator_expander = st.expander("✅ Modus file validator", expanded=False)

# Place the entire code block inside the expander
with xml_validator_expander:
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
            etree.parse(BytesIO(xml_data), xml_parser)
            return True, None
        except etree.XMLSchemaError as e:
            return False, str(e)
        except etree.XMLSyntaxError as e:
            return False, str(e)

    # Upload the XML file
    uploaded_file = st.file_uploader("Upload your file to see if it's a valid Modus file.", type="xml")
    if uploaded_file is not None:
        xml_data = uploaded_file.read()

        # Set the schema file path
        schema_path = os.path.join("Data", "modus_result.xsd")

        is_valid, error_message = validate_xml(xml_data, schema_path)

        if is_valid:
            st.success("The XML file is valid.")
        else:
            st.error(f"Invalid XML file. Error message: {error_message}")

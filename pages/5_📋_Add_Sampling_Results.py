import pandas as pd
import streamlit as st

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
min_sample_id, max_sample_id = st.slider("Set SampleID range", 1, 500, (1, 500), 1)

# Filter soil test data based on SampleID range
soil_test_data = soil_test_data[(soil_test_data.SampleID >= min_sample_id) & (soil_test_data.SampleID <= max_sample_id)]

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
filtered_soil_test_data = soil_test_data[(soil_test_data['SampleID'] >= min_sample_id) & (soil_test_data['SampleID'] <= max_sample_id)]
filtered_soil_test_data = filtered_soil_test_data.drop(columns=['ID'], errors='ignore')  # Drop the 'ID' column if it exists
filtered_soil_test_data = filtered_soil_test_data.dropna(axis=1, how='all')  # Drop columns with all missing values
st.dataframe(filtered_soil_test_data)

# Display depth references
st.write("---")
st.write("Depth References")
for i, depth_ref in enumerate(depth_refs):
    depth_id = i + 1
    if i == 0:
        depth_id = 1
    st.write(f"<DepthRefs>\n"
             f"  <DepthRef DepthID=\"{depth_id}\">\n"
             f"    <Name>not provided</Name>\n"
             f"    <StartingDepth>{depth_ref['StartingDepth']}</StartingDepth>\n"
             f"    <EndingDepth>{depth_ref['EndingDepth']}</EndingDepth>\n"
             f"    <ColumnDepth>{depth_ref['ColumnDepth']}</ColumnDepth>\n"
             f"    <DepthUnit>{depth_ref['DepthUnit']}</DepthUnit>\n"
             f"  </DepthRef>\n"
             f"</DepthRefs>\n")



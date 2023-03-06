import streamlit as st
import pandas as pd
import base64

st.info("This app is under construction, but enjoy reviewing the randomized sample results")
st.title("Generate Modus Sampling Results")

# Create two empty columns to position the radio selections
col1, col2, *_ = st.columns([3, 1, 6])

# Radio button to select between LBS and PPM
with col1:
    unit = st.radio("Analysis recorded in:", ('LBS', 'PPM'))

# Radio button to select depth units
with col2:
    depth_unit = st.radio("Select depth units:", ("Inches", "Centimeters"))

# Dropdown to select the number of depths sampled
num_depths = st.selectbox("Select # of depths sampled:", [1, 2, 3, 4, 5])

# Create an empty list to store the maximum depths
max_depths = []

# Input boxes for the maximum depth for each sample
num_cols = min(num_depths, 20)
col_width = int(12/num_cols)
cols = st.columns(num_cols)
for i in range(num_depths):
    with cols[i % num_cols]:
        st.write(f'<span style="color: green">Sample {i+1}</span>', unsafe_allow_html=True)
        if depth_unit == "inches":
            max_depth = st.number_input(f"Max depth for sample {i+1} ({depth_unit}):", key=f"max_depth_{i}", value=0.0, min_value=None, max_value=None, step=0.1)
        else:
            max_depth = st.number_input(f"Max depth for sample {i+1} ({depth_unit}):", key=f"max_depth_{i}", value=0.0, min_value=None, max_value=None, step=0.01)
        max_depths.append(max_depth)

# CSV file path based on the selected unit of measurement
if unit == 'LBS':
    file_path = "Data/lbs.csv"
else:
    file_path = "Data/ppm.csv"

# Read the CSV file into a pandas DataFrame
df = pd.read_csv(file_path)

# Repeat rows based on the selected number of depths sampled
df = pd.concat([df]*num_depths, ignore_index=True)

# Add the depth ID column to the DataFrame
depth_ids = [i%num_depths+1 for i in range(df.shape[0])]
df.insert(0, "DepthID", depth_ids)

# Save CSV button
csv = df.to_csv(index=False)
b64 = base64.b64encode(csv.encode()).decode()
href = f'<a href="data:file/csv;base64,{b64}" download="sample_data.csv">Download CSV</a>'

# Display the DataFrame and the download link
st.write(df)
st.markdown(href, unsafe_allow_html=True)

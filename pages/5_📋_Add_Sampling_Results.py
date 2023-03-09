import streamlit as st

st.info("This app is under construction, but enjoy reviewing the randomized sample results")
st.title("Generate Modus Sampling Results")

# Create two columns to hold the radio buttons for selecting the analysis and depth units
col1, col2 = st.columns(2)

# Radio button to select between LBS and PPM
with col1:
    unit = st.radio("Analysis units:", ('LBS', 'PPM'))

# Radio button to select depth units
with col2:
    depth_unit = st.radio("Depth units:", ("Inches", "Centimeters"))

# Range sliders for setting min and max range of sample IDs
min_sample_id, max_sample_id = st.slider("Set SampleID range", 1, 500, (1, 500), 1)

# Dropdown to select the number of depths sampled
num_depths = st.selectbox("Unique depths collected at each sample", [0, 1, 2, 3, 4, 5], key='num_depths', index=0)

# Create an empty list to store the maximum depths
max_depths = [0.0]

# Create a list of default maximum depths
default_depths = [0, 6, 12, 18, 24, 30, 36]

# Create an empty list to store the maximum depths
max_depths = [0.0]

# Input boxes for the maximum depth for topsoil and subsoils
cols = st.columns(num_depths + 1)
with cols[0]:
    st.write(f'<span style="color: blue">Topsoil</span>', unsafe_allow_html=True)
    if depth_unit == "Inches":
        max_depth = st.number_input(f"Topsoil depth ({depth_unit}):", key=f"max_depth_0", value=default_depths[1])
    else:
        max_depth = st.number_input(f"Topsoil depth ({depth_unit}):", key=f"max_depth_0", value=default_depths[1])
    max_depths.append(max_depth)

if num_depths > 0:
    for i in range(1, num_depths+1):
        with cols[i]:
            st.write(f'<span style="color: blue">Subsoil {i}</span>', unsafe_allow_html=True)
            if depth_unit == "Inches":
                prev_max_depth = max_depths[i-1]
                max_depth = st.number_input(f"Depth ({depth_unit}):", key=f"max_depth_{i}", value=default_depths[i+1])
                max_depths.append(max_depth)
            else:
                prev_max_depth = max_depths[i-1]
                max_depth = st.number_input(f"Depth {i} ({depth_unit}):", key=f"max_depth_{i}", value=default_depths[i+1])
                max_depths[i] = max_depth
                
# Display the resulting DataFrame if the form has been submitted
        st.write("---")
        st.write("Sample Results")
        st.write("min_sample_id:", min_sample_id)
        st.write("max_sample_id:", max_sample_id)
        st.write("unit:", unit)
        st.write("depth_unit:", depth_unit)
        st.write("num_depths:", num_depths)
        st.write("max_depths:", max_depths)
        st.write("previous value:",prev_max_depth)

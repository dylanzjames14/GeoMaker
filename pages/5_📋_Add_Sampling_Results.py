import streamlit as st
import pandas as pd

st.info("This app is under construction, but enjoy reviewing the randomized sample results")
st.title("Add Sampling Results")

# Radio button to select between LBS and PPM
unit = st.radio("Select units", ('LBS', 'PPM'))

# Slider to select the range of rows to display
num_rows = st.slider("Select the number samples", 1, 100)

# CSV file path based on the selected unit of measurement
if unit == 'LBS':
    file_path = "Data/lbs.csv"
else:
    file_path = "Data/ppm.csv"

# Read the CSV file into a pandas DataFrame
df = pd.read_csv(file_path, nrows=num_rows+1)

# Display the DataFrame on the page
st.write(df.head(num_rows))

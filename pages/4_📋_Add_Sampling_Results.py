import streamlit as st
import pandas as pd

st.info("This app is under construction, but enjoy reviewing the randomized sample results")
st.title("Create A Modus File")
st.write("Create a Modus results XML file with specified sample IDs")


# Use the "../" notation to navigate to the parent directory
file_path = "https://github.com/dylanzjames14/GeoMaker/blob/17b1a69be76074f6f376eac579ed4a4d8d338574/Data/Mock%20Soil%20Test%20Data.xlsx"

# Read the Excel file into a pandas DataFrame
df = pd.read_excel(file_path)

# Display the DataFrame on the page
st.write(df)

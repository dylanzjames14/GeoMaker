import streamlit as st
import pandas as pd
import numpy as np

# Function to calculate the total amount of product needed
def calculate_total(rate, area, conversion_factor):
    return round(rate * area * conversion_factor, 2)

# Function to calculate the total amount of product needed for units with a carrier
def calculate_total_concentration(rate, carrier_rate, conversion_factor):
    return round(rate * carrier_rate * conversion_factor, 2)

# Dictionary for conversion factors with the new units
conversion_factors = {
    "Seed/ac": 1,
    "kseed/ac": 1,
    "plant/ac": 1,
    "tree/ac": 1,
    "Seed/ha": 0.404686,
    "kseed/ha": 0.404686,
    "plant/ha": 0.404686,
    "tree/ha": 0.404686,
    "plant/ft2": 43.560,
    "plant/m2": 10.764,
    "gal/ac": 1,
    "fluid oz/ac": 128,
    "Liquid pint/ac": 8,
    "Liquid quart/ac": 4,
    "Imp. Gal/ac": 1.201,
    "Litre/ac": 3.78541,
    "ml/ac": 3785.41,
    "Megalitre/ac": 0.00000378541,
    "acre in/ac": 27154.3,
    "fluid oz/1000 ft2": 43.560,
    "gal/1000 ft2": 43.560,
    "Imp. Gal/1000 ft2": 43.560 * 1.201,
    "Imp. Gal/ft2": 1.201,
    "Imp. Gal/mi2": 2589988.110336,
    "Imp. Gal/yd2": 1.1959900463011,
    "Litre/ha": 0.404686,
    "L/m2": 10.764,
    "m3/m2": 10.764,
    "Megalitre/ha": 0.000404686,
    "ml/ha": 404.686,
    "Imp. Gal/Ha": 0.484,
    "Imp. Gal/km2": 2.589988110336,
    "Imp. Gal/m2": 10.764,
    "lbs/ac": 1,
    "oz(dry)/ac": 16,
    "U.S. ton/ac": 0.0005,
    "grams/ac": 453.592,
    "cwt/ac": 0.02,
    "cwt/ha": 0.008112,
    "kg/ac": 0.453592,
    "metric ton/ac": 0.000453592,
    "kg/ha": 0.404686,
    "metric ton/ha": 0.000404686,
    "grams/ha": 404.686,
    "kg/m2": 10.764,
    "lb/1000 ft2": 43.560,
    "U.S. ton/ha": 0.89218,
}


# Get the units that require a carrier for conversion
units_with_carrier = ["fluid oz/100 gal", "liquid pint/100 gal", "liquid quart/100 gal", "gal/100 gal", "fluid oz / bu", "ml/100 gal", "litre/100L", "ml/100L", "m3/m3", "lb/cwt", "lbs/lb", "lbs/ton", "oz/cwt", "oz(dry)/Ton", "kg/100kg", "kg/metric ton", "kg/kg", "grams/kg", "mg/kg", "grams/kg", "kg/100kg", "kg/kg", "kg/metric ton", "lb/cwt", "lbs/lb", "lbs/ton", "mg/kg", "oz/cwt", "oz/cwt", "oz(dry)/Ton"]

st.title("Agricultural Rate Unit Converter")
st.write("This application converts rate units to their total for agricultural applications.")

# User inputs
rate = st.number_input("Enter the application rate:", min_value=0.0)
area = st.number_input("Enter the area to be treated (in acres, hectares, etc.):", min_value=0.0)
unit_conversion = st.selectbox("Select the conversion unit:", list(conversion_factors.keys()))

carrier_rate = None
if unit_conversion in units_with_carrier:
    carrier_options = ["gal/ac", "L/ha", "U.S. Ton/ac", "Metric ton/ha"]
    carrier_unit = st.selectbox("Select the carrier unit:", carrier_options)
    carrier_rate = st.number_input(f"Enter the carrier rate (in {carrier_unit}):", min_value=0.0)

# Calculate and display the total
if st.button("Calculate"):
    conversion_factor = conversion_factors[unit_conversion]
    
    if carrier_rate is not None:
        total = calculate_total_concentration(rate, carrier_rate, conversion_factor)
        st.success(f"The total amount of product needed is {total} {unit_conversion.split('/')[0]}")
    else:
        total = calculate_total(rate, area, conversion_factor)
        st.success(f"The total amount of product needed is {total} {unit_conversion.split('/')[0]}")

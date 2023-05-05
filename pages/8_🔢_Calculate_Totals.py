import streamlit as st

# Dictionary containing most common agricultural fertilizers in the United States
# Dictionary containing common agricultural fertilizers
fertilizers = {
    "Urea (46-0-0)": {"N": 46, "P": 0, "K": 0},
    "Ammonium Nitrate (34-0-0)": {"N": 34, "P": 0, "K": 0},
    "Monoammonium Phosphate (11-52-0)": {"N": 11, "P": 52, "K": 0},
    "Diammonium Phosphate (18-46-0)": {"N": 18, "P": 46, "K": 0},
    "Triple Superphosphate (0-46-0)": {"N": 0, "P": 46, "K": 0},
    "Muriate of Potash (0-0-60)": {"N": 0, "P": 0, "K": 60},
    "Sulfate of Potash (0-0-50)": {"N": 0, "P": 0, "K": 50},
    "Potassium Nitrate (13-0-46)": {"N": 13, "P": 0, "K": 46},
    "Ammonium Sulfate (21-0-0-24S)": {"N": 21, "P": 0, "K": 0, "S": 24},
    "Calcium Nitrate (15.5-0-0)": {"N": 15.5, "P": 0, "K": 0},
    "Sodium Nitrate (16-0-0)": {"N": 16, "P": 0, "K": 0},
    "Magnesium Sulfate (0-0-0-9.8Mg-13S)": {"N": 0, "P": 0, "K": 0, "Mg": 9.8, "S": 13},
    "Gypsum (0-0-0-23Ca-18S)": {"N": 0, "P": 0, "K": 0, "Ca": 23, "S": 18},
    "Calcium Ammonium Nitrate (27-0-0)": {"N": 27, "P": 0, "K": 0},
    "Ammonium Polyphosphate (10-34-0)": {"N": 10, "P": 34, "K": 0},
    "Ammonium Thiosulfate (12-0-0-26S)": {"N": 12, "P": 0, "K": 0, "S": 26},
    "Borax (0-0-0-10B)": {"N": 0, "P": 0, "K": 0, "B": 10},
    "Mono Potassium Phosphate (0-52-34)": {"N": 0, "P": 52, "K": 34},
    "Dolomite (0-0-0-20Ca-10Mg)": {"N": 0, "P": 0, "K": 0, "Ca": 20, "Mg": 10},
}

def calculate_total_nutrition(product, rate):
    nutrients = fertilizers[product]
    total_nutrition = {key: value * rate / 100 for key, value in nutrients.items()}
    return total_nutrition

st.title("Fertilizer Nutrition Calculator")
st.write("Select fertilizers and their respective rates to calculate the total nutrition.")

selected_fertilizers = st.multiselect("Fertilizers", list(fertilizers.keys()))

rate_unit = st.selectbox("Unit", ["Pounds per Acre", "Gallons per Acre"])

rates = {}
for fertilizer in selected_fertilizers:
    rate = st.number_input(f"Rate for {fertilizer}", min_value=0.0, step=0.1)
    rates[fertilizer] = rate

if st.button("Calculate"):
    total_nutrition = {"N": 0, "P": 0, "K": 0}
    for fertilizer, rate in rates.items():
        if rate_unit == "Gallons per Acre":
            rate *= 8.345  # Convert gallons to pounds assuming water-like density
        nutrition = calculate_total_nutrition(fertilizer, rate)
        for nutrient in total_nutrition:
            total_nutrition[nutrient] += nutrition[nutrient]

    st.write(f"Total nutrition for the selected fertilizers at their respective rates (in {rate_unit}):")
    st.write(f"Nitrogen (N): {total_nutrition['N']} lbs/acre")
    st.write(f"Phosphorus (P): {total_nutrition['P']} lbs/acre")
    st.write(f"Potassium (K): {total_nutrition['K']} lbs/acre")

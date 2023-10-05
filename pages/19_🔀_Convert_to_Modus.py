import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="🌱 Modus Soil Test Converter 🌱",
    layout="wide"
)
st.warning("🚧 This tool is still under construction and may not be fully functional yet. Use with caution! 🚧")
st.title("🌱 Modus Soil Test Converter 🌱")
st.write("""
Welcome to the Modus Soil Test Converter! 🌍 Transform your soil test data into the standardized Modus format with just a few clicks. Say goodbye to the hassle of manual conversions!
""")

soil_test_analysis = [
    "ACE nitrogen (soil protein index)",
    "acidity",
    "adjusted sodium adsorption ratio",
    "aggregate stability",
    "aluminum",
    "amino nitrogen",
    "ammonium",
    "ammonium-nitrogen",
    "antimony",
    "arsenic",
    "arylsulfatase",
    "available water holding capacity",
    "barium",
    "base saturation",
    "base saturation - Ca",
    "base saturation - H",
    "base saturation - K",
    "base saturation - Mg",
    "base saturation - Na",
    "base saturation - Ca:Mg",
    "base saturation - Mg:K",
    "base saturation - K:Mg",
    "base saturation - Ca+Mg",
    "beta-glucosidase",
    "bicarbonate",
    "boron",
    "buffer pH",
    "bulk density",
    "C:N ratio",
    "Ca + exchangable Mg",
    "Ca:K ratio",
    "Ca:Mg ratio",
    "Ca:NO3 ratio",
    "Ca+Mg:K ratio",
    "cadmium",
    "calcium",
    "calcium carbonate",
    "carbon",
    "carbon, total",
    "carbonate",
    "carbonates, qualitative",
    "cation exchange capacity",
    "cation ratio of structural stability",
    "cation:anion ratio",
    "chloride",
    "chromium",
    "clay",
    "CO2 respiration",
    "cobalt",
    "color",
    "copper",
    "copper index",
    "deleterious material",
    "dispersion index",
    "dissolved organic nitrogen (DON)",
    "electrical conductivity",
    "electrochemical stability index",
    "emerson class",
    "estimated nitrogen release",
    "exchangeable acidity",
    "exchangeable aluminum",
    "exchangeable calcium percentage",
    "exchangeable hydrogen",
    "exchangeable hydrogen percentage",
    "exchangeable magnesium percentage",
    "exchangeable potassium percentage",
    "exchangeable sodium percentage",
    "fluoride",
    "genomics",
    "grass tetany risk index",
    "gravel",
    "gypsum recommendation",
    "H+EALP",
    "humic matter",
    "hydrogen+aluminum",
    "hydroxide",
    "iron",
    "K:B ratio",
    "K:Mg ratio",
    "K:Na ratio",
    "lead",
    "lime index",
    "lime recommendation",
    "lithium",
    "magnesium",
    "magnesium index",
    "manganese",
    "manganese index",
    "mercury",
    "Mg:K ratio",
    "Mn:Cu ratio",
    "Mn:Zn ratio",
    "moisture content",
    "molybdenum",
    "N-acetyl-β-D-glucosaminidase (NAG)",
    "nickel",
    "nitrate",
    "nitrate-nitrogen",
    "nitrite-nitrogen",
    "nitrogen mineralization rate",
    "nitrogen, total",
    "nitrogen, total inorganic",
    "organic carbon",
    "organic carbon, total",
    "organic matter",
    "organic nitrogen",
    "other",
    "P:Cu ratio",
    "P:Mn ratio",
    "P:S ratio",
    "P:Zn ratio",
    "particle density",
    "particulate organic matter 53-2000 um",
    "permanganate-oxidizable carbon (POXC)",
    "pH",
    "phosphate",
    "phospholipid fatty acid (PLFA)",
    "phosphomonoesterase",
    "phosphorus",
    "phosphorus buffer index",
    "phosphorus environmental risk index",
    "phosphorus fixation factor",
    "phosphorus index",
    "phosphorus ratio",
    "phosphorus retention index",
    "phosphorus saturation index",
    "phosphorus, total",
    "potassium",
    "potassium",
    "potassium fixation factor",
    "potassium index",
    "potassium, total",
    "potential mineralizable nitrogen",
    "potential oxidizable carbon",
    "potentially mineralizable nitrogen (PMN)",
    "reflectance",
    "rootzone moisture",
    "sand",
    "sand - coarse",
    "sand - fine",
    "sand - medium",
    "sand - very coarse",
    "sand - very fine",
    "saturated hydraulic conductivity",
    "saturation paste %",
    "selenium",
    "short-term carbon mineralization",
    "silicon",
    "silt",
    "silt+clay",
    "silver",
    "slaking",
    "sodium",
    "sodium adsorption ratio",
    "solids, total",
    "soluble salts",
    "soluble salts index",
    "strontium",
    "sulfate-sulfur",
    "sulfur",
    "sulfur index",
    "textural classification",
    "tin",
    "titratable acidity",
    "total carbon:total nitrogen",
    "total organic carbon: total nitrogen",
    "unknown",
    "urea",
    "water extractable nitrogen (WEN)",
    "water extractable organic carbon (WEOC)",
    "water extractable organic nitrogen (TDN)",
    "water extractable organic nitrogen (WEON)",
    "water soluble C:N ratio",
    "water soluble carbon",
    "water-soluble organic carbon (WSOC)",
    "zinc",
    "zinc index",
    "Zn:Cu ratio"
]


def main():
    
    # Upload the file
    file = st.file_uploader("Choose a CSV, TXT, DBF or other delimited file", type=['csv', 'txt', 'dbf'])
    
    # Check if a file is uploaded
    if file:
        # Use an expander for file configurations
        with st.expander("File Configuration", expanded=True):
            # Choose delimiter
            delimiter = st.selectbox("Choose the delimiter:", [",", ";", "\t", "|", "Other"])
            if delimiter == "Other":
                delimiter = st.text_input("Specify the delimiter:", value=",")
            
            # Check for headers (unselected by default)
            header = st.checkbox("Does the file have a header?", value=False)
        
        # Load the data
        if header:
            data = pd.read_csv(file, delimiter=delimiter)
        else:
            data = pd.read_csv(file, delimiter=delimiter, header=None)
        
        # Display the data
        st.write(data)
        
        # Display dropdowns for matching columns
        st.subheader("Match Columns to Soil Test Analysis Types")
        matched_columns = {}
        cols = st.columns(5)  # Five columns for dropdowns
        for idx, col_name in enumerate(data.columns):
            with cols[idx % 5]:
                selected_analysis = st.selectbox(f"Match column '{col_name}':", options=soil_test_analysis, index=0)
                matched_columns[col_name] = selected_analysis
        st.write("Matched Results:", matched_columns)

if __name__ == "__main__":
    main()

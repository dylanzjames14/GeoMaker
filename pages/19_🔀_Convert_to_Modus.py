import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="🔀 Modus Soil Test Converter 🔀",
    layout="wide"
)

st.title("🔀 Modus Soil Test Converter 🔀")
st.write("""
Welcome to the Modus Soil Test Converter! Transform your soil test data into the standardized Modus format with just a few clicks. Say goodbye to the hassle of manual conversions!
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

default_units = {
    "ACE nitrogen (soil protein index)": ['g/kg'],
    "acidity": ['mg/kg', 'meq/cmol'],
    "adjusted sodium adsorption ratio": ['Ratio'],
    "aggregate stability": ['%'],
    "aluminum": ['meq/100g', 'mg/dm3', 'ppm', 'mg/kg', '%', 'cmol/kg', 'mg/L', 'mg/m2'],
    "amino nitrogen": [],
    "ammonium": ['mg/m2'],
    "ammonium-nitrogen": ['mg/L', 'mg/kg', 'ppm'],
    "antimony": ['mg/kg', 'ppm'],
    "arsenic": ['ug/kg', 'mg/kg', 'ppm', 'ppb'],
    "arylsulfatase": ['nmol/h/mg'],
    "available water holding capacity": ['mg/kg', 'ppm'],
    "barium": ['ppm', 'mg/kg'],
    "base saturation": ['%'],
    "base saturation - Ca": ['%'],
    "base saturation - H": ['%'],
    "base saturation - K": ['%'],
    "base saturation - Mg": ['%'],
    "base saturation - Na": ['%'],
    "base saturation - Ca:Mg": ['None'],
    "base saturation - Mg:K": ['None'],
    "base saturation - K:Mg": ['None'],
    "base saturation - Ca+Mg": ['None'],
    "beta-glucosidase": ['U/mg'],
    "bicarbonate": ['meq/L'],
    "boron": ['mg/dm3', 'mg/kg', 'ppm', 'meq/L', 'mg/m2'],
    "buffer pH": ['standard pH unit'],
    "bulk density": ['g/cm3'],
    "C:N ratio": ['Ratio'],
    "Ca + exchangable Mg": [],
    "Ca:K ratio": [],
    "Ca:Mg ratio": [],
    "Ca:NO3 ratio": [],
    "Ca+Mg:K ratio": [],
    "cadmium": ['ug/kg', 'ppm', 'mg/kg', 'ppb', 'mg/m2'],
    "calcium": ['meq/100g', 'None', 'mg/dm3', 'ppm', 'mg/kg', '%', 'cmol/kg', 'meq/L', 'mg/m2'],
    "calcium carbonate": ['%'],
    "carbon": ['mg/kg', 'ppm'],
    "carbon, total": ['%'],
    "carbonate": ['meq/L', '%'],
    "carbonates, qualitative": ['None'],
    "cation exchange capacity": ['meq/100g', 'mg/kg', 'ppm', 'cmol/kg'],
    "cation ratio of structural stability": ['None'],
    "cation:anion ratio": [],
    "chloride": ['mg/L', 'mg/kg', 'ppm', 'meq/L'],
    "chromium": ['ug/kg', 'ppm', 'mg/kg', 'ppb'],
    "clay": ['%'],
    "CO2 respiration": ['mg/g'],
    "cobalt": ['ug/kg', 'mg/kg', 'ppm', 'ppb', 'mg/L'],
    "color": ['None'],
    "copper": ['mg/m2', 'ppm', 'mg/kg', 'mg/dm3'],
    "copper index": ['None'],
    "deleterious material": ['%'],
    "dispersion index": ['None'],
    "dissolved organic nitrogen (DON)": ['mg/kg', 'ppm'],
    "electrical conductivity": ['mmho/cm', 'dS/m'],
    "electrochemical stability index": ['None'],
    "emerson class": ['None'],
    "estimated nitrogen release": ['lb/ac', 'kg/ha'],
    "exchangeable acidity": ['cmol/kg', 'meq/100 g'],
    "exchangeable aluminum": ['%'],
    "exchangeable calcium percentage": ['%'],
    "exchangeable hydrogen": ['meq/100 g', 'cmol/kg'],
    "exchangeable hydrogen percentage": ['%'],
    "exchangeable magnesium percentage": ['%'],
    "exchangeable potassium percentage": ['%'],
    "exchangeable sodium percentage": ['%'],
    "fluoride": ['mg/L'],
    "genomics": [],
    "grass tetany risk index": ['None'],
    "gravel": ['%'],
    "gypsum recommendation": ['tons/ac'],
    "H+EALP": ['none'],
    "humic matter": ['%'],
    "hydrogen+aluminum": ['meq/100 g'],
    "hydroxide": ['mg/L'],
    "iron": ['mg/dm3', 'mg/kg', 'ppm', 'mg/L', 'mg/m2'],
    "K:B ratio": ['ppm', 'none'],
    "K:Mg ratio": ['None'],
    "K:Na ratio": ['ppm', 'none'],
    "lead": ['ug/kg', 'mg/kg', 'ppm', 'ppb', 'mg/m2'],
    "lime index": ['None'],
    "lime recommendation": ['kg/ha', 'tons/ac'],
    "lithium": ['mg/kg', 'ppm'],
    "magnesium": ['meq/100g', 'mg/dm3', 'mg/kg', 'ppm', 'cmol/kg', '%', 'meq/L', 'mg/m2'],
    "magnesium index": ['None'],
    "manganese": ['mg/dm3', 'ppm', 'mg/kg', 'mg/L', 'mg/m2'],
    "manganese index": ['None'],
    "mercury": ['mg/kg', 'ppm'],
    "Mg:K ratio": ['None'],
    "Mn:Cu ratio": ['ppm', 'none'],
    "Mn:Zn ratio": ['ppm', 'none'],
    "moisture content": ['in/ft', '%'],
    "molybdenum": ['ug/kg', 'mg/dm3', 'ppm', 'mg/kg', 'ppb', 'mg/L', 'mg/m2', 'ug/10cm2'],
    "N-acetyl-β-D-glucosaminidase (NAG)": ['nmol/h/mg'],
    "nickel": ['mg/kg', 'ppm'],
    "nitrate": ['mg/m2'],
    "nitrate-nitrogen": ['mg/L', 'mg/kg', 'ppm', 'meq/L'],
    "nitrite-nitrogen": ['mg/kg', 'ppm'],
    "nitrogen mineralization rate": ['mg/kg', 'ppm'],
    "nitrogen, total": ['kg/ha/day', 'lb/ac/day', '%'],
    "nitrogen, total inorganic": ['mg/kg', 'ppm'],
    "nan": ['None'],
    "organic carbon": ['mg/kg', 'ppm', '%'],
    "organic carbon, total": ['%', 'g/kg'],
    "organic matter": ['%'],
    "organic nitrogen": ['mg/L'],
    "other": ['None'],
    "P:Cu ratio": ['ppm', 'none'],
    "P:Mn ratio": ['ppm', 'none'],
    "P:S ratio": ['ppm', 'none'],
    "P:Zn ratio": ['ppm', 'none'],
    "particle density": ['g/cm3'],
    "particulate organic matter 53-2000 um": ['g/kg'],
    "permanganate-oxidizable carbon (POXC)": ['ppm', 'mg/kg'],
    "pH": ['mg/kg', 'ppm', 'standard pH unit'],
    "phosphate": ['mg/kg', 'ppm'],
    "phospholipid fatty acid (PLFA)": ['ng/g'],
    "phosphomonoesterase": ['ug/g', 'mg/kg, ppm'],
    "phosphorus": ['mg/dm3', 'ppm', 'mg/kg', '%', 'mg/L', 'mg/m2'],
    "phosphorus buffer index": ['ppm', 'mg/kg'],
    "phosphorus environmental risk index": ['mg/kg', 'ppm'],
    "phosphorus fixation factor": ['mg/kg', 'ppm'],
    "phosphorus index": ['mg/kg', 'ppm'],
    "phosphorus ratio": ['None'],
    "phosphorus retention index": ['mg/kg', 'ppm'],
    "phosphorus saturation index": ['ppm', 'mg/kg'],
    "phosphorus, total ": ['ppm', 'mg/kg'],
    "potassium": ['mg/dm3', 'ppm', 'mg/kg', '%', 'cmol/kg', 'meq/100 g', 'meq/L', 'mg/m2'],
    "potassium ": ['ppm', 'mg/kg'],
    "potassium fixation factor": ['%'],
    "potassium index": ['None'],
    "potassium, total ": ['mg/kg', 'ppm'],
    "potential mineralizable nitrogen": ['mg/kg', 'ppm'],
    "potential oxidizable carbon": ['mg/kg', 'ppm'],
    "potentially mineralizable nitrogen (PMN)": ['mg/kg', 'ppm'],
    "reflectance": ['Reflectance percentage (R%)'],
    "rootzone moisture": ['%'],
    "sand": ['%'],
    "sand - coarse": ['%'],
    "sand - fine": ['%'],
    "sand - medium": ['%'],
    "sand - very coarse": ['%'],
    "sand - very fine": ['%'],
    "saturated hydraulic conductivity": ['in/hr', 'cm3/hr'],
    "saturation paste %": ['%'],
    "selenium": ['ug/kg', 'ppm', 'mg/kg', 'ppb'],
    "short-term carbon mineralization": ['mg/kg'],
    "silicon": ['mg/L', 'ppm', 'mg/kg'],
    "silt": ['%'],
    "silt+clay": ['%'],
    "silver": ['mg/kg', 'ppm'],
    "slaking": ['None'],
    "sodium": ['mg/dm3', 'ppm', 'mg/kg', '%', 'cmol/kg', 'meq/100 g', 'mg/L', 'lb/ac', 'meq/L'],
    "sodium adsorption ratio": ['None', 'Ratio', 'ratio'],
    "solids, total": ['%'],
    "soluble salts": ['mg/kg', 'ppm'],
    "soluble salts index": ['None'],
    "strontium": ['ppm', 'mg/kg'],
    "sulfate-sulfur": ['mg/L', 'mg/kg', 'ppm', 'meq/L'],
    "sulfur": ['kg/ha', 'mg/dm3', 'ppm', 'mg/kg', '%', 'lb/ac', 'meq/L', 'mg/m2'],
    "sulfur index": ['None'],
    "textural classification": ['None', 'Texture Classification'],
    "tin": ['mg/kg', 'ppm'],
    "titratable acidity": ['cmol/kg', 'meq/100 g'],
    "total carbon:total nitrogen": ['none'],
    "total organic carbon: total nitrogen": ['none'],
    "unknown": ['None'],
    "urea": ['mg/kg', 'ppm'],
    "water extractable nitrogen (WEN)": ['mg/kg', 'ppm'],
    "water extractable organic carbon (WEOC)": ['g'],
    "water extractable organic nitrogen (TDN)": ['mg/g'],
    "water extractable organic nitrogen (WEON)": ['mg/kg', 'ppm'],
    "water soluble C:N ratio": ['ratio'],
    "water soluble carbon": ['mg/kg', 'ppm'],
    "water-soluble organic carbon (WSOC)": ['mg/kg', 'ppm'],
    "zinc": ['mg/dm3', ' ', 'ppm', 'mg/kg', 'mg/L', 'mg/m2', 'ug/10cm2'],
    "zinc index": ['None'],
    "Zn:Cu ratio": ['ppm', 'none'],}

def main():
    
    # Upload the file
    file = st.file_uploader("Choose a CSV, TXT, DBF or other delimited file", type=['csv', 'txt', 'dbf'])
    
    # Initialize sample_id_col here
    sample_id_col = ''  
    
    matched_columns = {}
    unit_columns = {}

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

        # Display dropdown for Sample ID
        sample_id_col = st.selectbox("Choose the 'Sample ID' column:", options=[''] + list(data.columns), key="sample_id_selectbox")
        
        # Display the data before starting the matching process
        st.write(data)

        # Reset selections button
        if st.button("Reset Selections"):
            st.experimental_rerun()

        # Create a container for the scrollable section
        container = st.container()
        
        for col_name in sorted(data.columns):  # Sort by column names
            if col_name != sample_id_col:
                with container:
                    cols = st.columns(3)  # Three columns: column name, analysis dropdown, units dropdown
                    cols[0].write(col_name)
                    selected_analysis = cols[1].selectbox("Analysis", options=['Select Analysis Type'] + soil_test_analysis, key=f"analysis_{col_name}")
                    if selected_analysis != 'Select Analysis Type':
                        matched_columns[col_name] = selected_analysis

                        # Display units dropdown if there are units available for the selected analysis
                        if selected_analysis in default_units and default_units[selected_analysis]:
                            selected_unit = cols[2].selectbox("Unit", options=['Select Unit'] + default_units[selected_analysis], key=f"unit_{col_name}")
                            if selected_unit != 'Select Unit':
                                unit_columns[col_name] = selected_unit

        # Convert the entire dataframe to strings to ensure consistent data types
        data = data.astype(str)

        # Update the dataframe with matched analysis and units
        unit_row = [unit_columns.get(col, '') for col in data.columns]
        data.loc[-1] = unit_row
        data.index = data.index + 1

        analysis_row = [matched_columns.get(col, '') for col in data.columns]
        data.loc[-2] = analysis_row
        data.index = data.index + 1

        data = data.sort_index()

        # Redisplay the data with the matched analysis and units
        st.write(data)

if __name__ == "__main__":
    main()

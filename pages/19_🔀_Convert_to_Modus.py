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

soil_test_analysis = {
'ACE nitrogen (soil protein index)': [''],
'C:N ratio': ['S-C:N.16'],
'CO2 respiration': ['S-CO2-RESP.01'],
'Ca + exchangable Mg': ['S-CAEMG-M1.19'],
'Ca+Mg:K ratio': ['S-CAMG:KM1.19'],
'Ca:K ratio': ['S-CA:KM1.19'],
'Ca:Mg ratio': ['S-CA:MG.19'],
'Ca:NO3 ratio': ['S-CA:NO3.19'],
'H+EALP': ['S-HEAL-SMP.19'],
'K:B ratio': ['S-K:B.19'],
'K:Mg ratio': ['S-K:MG-PWAA.19'],
'K:Na ratio': ['S-K:Na-M3.19'],
'Mg:K ratio': ['S-MG:K.19'],
'Mn:Cu ratio': ['S-Mn:Cu-M3.19'],
'Mn:Zn ratio': ['S-Mn:Zn-M3.19'],
'N-acetyl-β-D-glucosaminidase (NAG)': [''],
'P:Cu ratio': ['S-P:Cu-M3.19'],
'P:Mn ratio': ['S-P:Mn-M3.19'],
'P:S ratio': ['S-P:S-M3.19'],
'P:Zn ratio': ['S-P:Zn-M3.19'],
'Zn:Cu ratio': ['S-Zn:Cu-M3.19'],
'acidity': ['S-Acidity.19'],
'adjusted sodium adsorption ratio': ['S-SARJ-SP.00'],
'aggregate stability': [''],
'aluminum': ['S-AL-BACL2.23'],
'amino nitrogen': ['S-AN-12.00'],
'ammonium': [''],
'ammonium-nitrogen': ['S-NH4N-W1:1.01'],
'antimony': ['S-SB-EPA3050.04'],
'arsenic': ['S-AS-AR.07'],
'arylsulfatase': [''],
'available water holding capacity': [''],
'barium': ['S-BA-EPA3050.04'],
'base saturation': ['S-BS.19'],
'base saturation - Ca': ['S-BS-CA.19'],
'base saturation - Ca+Mg': [''],
'base saturation - Ca:Mg': [''],
'base saturation - H': ['S-BS-H.19'],
'base saturation - K': ['S-BS-K.19'],
'base saturation - K:Mg': [''],
'base saturation - Mg': ['S-BS-MG.19'],
'base saturation - Mg:K': [''],
'base saturation - Na': ['S-BS-NA.19'],
'beta-glucosidase': [''],
'bicarbonate': ['S-HCO3-SP.19'],
'boron': ['S-B-CACL2.23'],
'buffer pH': ['S-BPH-AEB.02'],
'bulk density': ['S-BD-Clod.00'],
'cadmium': ['S-CD-AR.07'],
'calcium': ['S-CA-PWAA.23'],
'calcium carbonate': ['S-CACO3-AA.02'],
'carbon': ['S-C-W-04'],
'carbon, total': ['S-TC-COMB.15'],
'carbonate': ['S-CO3-AA.02'],
'carbonates, qualitative': ['S-CACO3.11'],
'cation exchange capacity': ['S-CEC-AA.23'],
'cation ratio of structural stability': ['S-CROSS-W5:1.19'],
'cation:anion ratio': ['S-C:A.19'],
'chloride': ['S-CL-HG.01'],
'chromium': ['S-CR-AR.07'],
'clay': ['S-CLAY-SV.19'],
'cobalt': ['S-CO-AR.07'],
'color': ['S-Color.24'],
 'copper': ['S-CU-DTPA.05'],
 'copper index': ['S-CU-NCINDX'],
 'deleterious material': ['S-DM.15'],
 'dispersion index': ['S-DI.24'],
 'dissolved organic nitrogen (DON)': [''],
 'electrical conductivity': ['S-EC-1:1.03'],
 'electrochemical stability index': ['S-ESI.19'],
 'emerson class': ['S-EMERSON.19'],
 'estimated nitrogen release': ['S-ENR.19'],
 'exchangeable acidity': ['S-AC-KCL.12'],
 'exchangeable aluminum': ['S-EAL-KCL.19'],
 'exchangeable calcium percentage': ['S-ECAP.19'],
 'exchangeable hydrogen': ['S-EH-KCL.12'],
 'exchangeable hydrogen percentage': ['S-EHP.19'],
 'exchangeable magnesium percentage': ['S-EMGP.19'],
 'exchangeable potassium percentage': ['S-EKP.19'],
 'exchangeable sodium percentage': ['S-ESP.19'],
 'fluoride': ['S-F-EPA3000.00'],
 'genomics': [''],
 'grass tetany risk index': ['S-GTRI-PWAA.19'],
 'gravel': ['S-GRAVEL.19'],
 'gypsum recommendation': ['S-GYPR.19'],
 'humic matter': ['S-HA-FSPA.01'],
 'hydrogen+aluminum': ['S-H+AL-SMP.02'],
 'hydroxide': ['S-OH-SM2320B18.12'],
 'iron': ['S-FE-OX.23'],
 'lead': ['S-PB-AR.07'],
 'lime index': ['S-LIME-INDX.19'],
 'lime recommendation': ['S-LR-AEB'],
 'lithium': ['S-LI-EPA3050.04'],
 'magnesium': ['S-MG-PWAA.23'],
 'magnesium index': ['S-MG-INDX.19'],
 'manganese': ['S-MN-DTPA.05'],
 'manganese index': ['S-MN-NCINDX'],
 'mercury': ['S-HG-EPA3050.04'],
 'moisture content': ['S-MOIST-GRAV.00'],
 'molybdenum': ['S-MO-OA.04'],
 'nickel': ['S-NI-EPA6010B.00'],
 'nitrate': [''],
 'nitrate-nitrogen': ['S-NO3N-ALSO4B.02'],
 'nitrite-nitrogen': ['S-NO2-KCL.01'],
 'nitrogen mineralization rate': [''],
 'nitrogen, total': ['S-TKN.01'],
 'nitrogen, total inorganic': ['S-TIN.19'],
 'organic carbon': ['S-TOC.16'],
 'organic carbon, total': ['S-TOC.12.09'],
 'organic matter': ['S-OM.19'],
 'organic nitrogen': ['S-ON.19'],
 'other': ['S-OTHER.19'],
 'pH': ['S-PH-1:1.02.08'],
 'particle density': [''],
 'particulate organic matter 53-2000 um': [''],
 'permanganate-oxidizable carbon (POXC)': ['S-AC-KMNO4.01'],
 'phosphate': [''],
 'phospholipid fatty acid (PLFA)': [''],
 'phosphomonoesterase': [''],
 'phosphorus': ['S-P-AA-NH4AC.04'],
 'phosphorus buffer index': ['S-PBI.19'],
 'phosphorus environmental risk index': ['S-PERI.19'],
 'phosphorus fixation factor': ['S-PFF-M3.04'],
 'phosphorus index': ['S-P-INDX'],
 'phosphorus ratio': ['S-PR-M3.23'],
 'phosphorus retention index': ['S-PRI-KCL.01'],
 'phosphorus saturation index': ['S-PSI.M3.19'],
 'phosphorus, total ': ['S-TP-H2SO4.01'],
 'potassium': ['S-K-PWAA.23'],
 'potassium ': ['S-K-EPA3050.04'],
 'potassium fixation factor': ['S-KFF-M3.04'],
 'potassium index': ['S-K-INDX.19'],
 'potassium, total ': ['S-TKP.01'],
 'potential mineralizable nitrogen': ['S-PMN.01.0'],
 'potential oxidizable carbon': ['S-POXC.01.0'],
 'potentially mineralizable nitrogen (PMN)': [''],
 'reflectance': [''],
 'rootzone moisture': ['S-RZM.00'],
 'sand': ['S-SAND-SV.19'],
 'sand - coarse': ['S-SANDC.BAL.19'],
 'sand - fine': ['S-SANDF.DAL.19'],
 'sand - medium': [''],
 'sand - very coarse': [''],
 'sand - very fine': [''],
 'saturated hydraulic conductivity': [''],
 'saturation paste %': ['S-SP%.19'],
 'selenium': ['S-SE-AR.07'],
 'short-term carbon mineralization': [''],
 'silicon': ['S-SI-AA.04'],
 'silt': ['S-SILT-SV.19'],
 'silt+clay': ['S-SI+C-SV'],
 'silver': ['S-AG-EPA3050.04'],
 'slaking': ['S-Slaking.24'],
 'sodium': ['S-NA-NH4AC.05'],
 'sodium adsorption ratio': ['S-SAR-AA.19'],
 'solids, total': ['S-SOLIDS.19'],
 'soluble salts': ['S-SS.19'],
 'soluble salts index': ['S-SS-NCINDX.19'],
 'strontium': ['S-SR-EPA3050.04'],
 'sulfate-sulfur': ['S-SO4-1:5.13'],
 'sulfur': ['S-S-NH4AC.04'],
 'sulfur index': ['S-S-NCINDX'],
 'textural classification': ['S-TEXTURE.19'],
 'tin': ['S-SN-EPA3050.04'],
 'titratable acidity': ['S-H-MEAS.12'],
 'total carbon:total nitrogen': ['S-TC:TN.19'],
 'total organic carbon: total nitrogen': ['S-TOC:TN.19'],
 'unknown': ['S-UNKNOWN.00'],
 'urea': ['S-UREA-NH4.01'],
 'water extractable nitrogen (WEN)': [''],
 'water extractable organic carbon (WEOC)': [''],
 'water extractable organic nitrogen (TDN)': [''],
 'water extractable organic nitrogen (WEON)': [''],
 'water soluble C:N ratio': [''],
 'water soluble carbon': ['S-SARJ-SP.00'],
 'water-soluble organic carbon (WSOC)': [''],
 'zinc': ['S-ZN-DTPA.05'],
 'zinc index': ['S-ZN-NCINDX']}

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

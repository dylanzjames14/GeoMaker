import streamlit as st
import pandas as pd
import xml.etree.ElementTree as ET
from xml.dom import minidom
import io

st.set_page_config(
    page_title="🔀 Modus Soil Test Converter 🔀",
    layout="wide"
)

st.title("🔀 Modus Soil Test Converter 🔀")
st.write("""
Welcome to the Modus Soil Test Converter! Transform your soil test data into the standardized Modus format with just a few clicks. Say goodbye to the hassle of manual conversions!
""")

# Warning message
st.warning("⚠️ This tool is still under development. Please verify results before use.")


# Instructions inside an expander
with st.expander("How to Use:", expanded=False):
    st.write("""
    1. **Upload** your soil test data file.
    2. **Match** the columns in your file to the Modus soil test analysis elements and units.
    3. **Convert** your data automatically converted to the Modus XML format.
    4. **Copy/Paste** the generated XML into your file.
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

soil_test_analysis_ref = {
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
    "buffer pH": ['None'],
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
    "pH": ['mg/kg', 'ppm', 'None'],
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


def convert_to_xml(data, matched_columns, unit_columns, sample_id_col, sample_date):
    xml_data = updated_generate_xml_v6(data, matched_columns, unit_columns, sample_id_col, sample_date)
    return xml_data

def prettify(elem):
    """Return a pretty-printed XML string for the Element."""
    rough_string = ET.tostring(elem, 'utf-8')
    reparsed = minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent="  ")

def updated_generate_xml_v6(data, matched_columns, unit_columns, sample_id_col, sample_date):
    root = ET.Element("ModusResult")
    
    # Event and its metadata
    event = ET.SubElement(root, "Event")
    event_metadata = ET.SubElement(event, "EventMetaData")
    ET.SubElement(event_metadata, "EventCode").text = "1234-ABCD"
    ET.SubElement(event_metadata, "EventDate").text = "2023-10-12"
    event_type = ET.SubElement(event_metadata, "EventType")
    ET.SubElement(event_metadata, "EventExpirationDate").text = "2023-10-19"

    # Lab metadata
    lab_metadata = ET.SubElement(event, "LabMetaData")
    ET.SubElement(lab_metadata, "LabName").text = "Geomaker Conversion"
    ET.SubElement(lab_metadata, "LabID").text = "1234567"
    ET.SubElement(lab_metadata, "LabEventID").text = "1234567"
    test_package_refs = ET.SubElement(lab_metadata, "TestPackageRefs")
    test_package_ref = ET.SubElement(test_package_refs, "TestPackageRef", {'TestPackageID': "1"})
    ET.SubElement(test_package_ref, "Name").text = "Unknown"
    ET.SubElement(test_package_ref, "LabBillingCode").text = "Unknown"
    ET.SubElement(lab_metadata, "ReceivedDate").text = "2023-10-12T00:00:00-06:00"
    ET.SubElement(lab_metadata, "ProcessedDate").text = "2023-10-12T00:00:00-06:00"
    
    # Reports
    reports = ET.SubElement(lab_metadata, "Reports")
    report = ET.SubElement(reports, "Report")
    ET.SubElement(report, "LabReportID")
    ET.SubElement(report, "FileDescription")
    ET.SubElement(report, "File")

    for _, row in data.iterrows():
        if sample_id_col not in row or pd.isnull(row[sample_id_col]):
            continue  # Skip the row if the sample_id_col is not present or is null
        
        soil_sample = ET.SubElement(root, "EventSample")
        
        samplemetadata = ET.SubElement(soil_sample, "SampleMetaData")
        ET.SubElement(samplemetadata, "SampleNumber").text = str(row[sample_id_col])
        ET.SubElement(samplemetadata, "OverwriteResult").text = "false"
        
        depths = ET.SubElement(soil_sample, "Depths")
        depth = ET.SubElement(depths, "Depth", DepthID="1")
        nutrient_results = ET.SubElement(depth, "NutrientResults")
        
        for col, value in row.items():
            if col != sample_id_col:
                if col in matched_columns:  # Only process columns that have been matched
                    nutrientresult = ET.SubElement(nutrient_results, "NutrientResult")
                    ET.SubElement(nutrientresult, "Element").text = matched_columns.get(col, "")
                    ET.SubElement(nutrientresult, "Value").text = str(value)
                    ET.SubElement(nutrientresult, "ModusTestID").text = soil_test_analysis_ref.get(matched_columns.get(col, ""), [""])[0]  # Use the ref for ModusTestID
                    ET.SubElement(nutrientresult, "ValueType").text = "Measured"
                    ET.SubElement(nutrientresult, "ValueUnit").text = unit_columns.get(col, "")  # Fetch the unit from the unit_columns dictionary
                    ET.SubElement(nutrientresult, "ValueDesc").text = "VL"  # Placeholder value, adjust if needed

    
    return prettify(root)

def main():
    # Initialize variables
    sample_id_col = ''  
    matched_columns = {}
    unit_columns = {}

    # Upload the file
    file = st.file_uploader("Choose a CSV, TXT, DBF or other delimited file", type=['csv', 'txt', 'dbf'])

    # Check if a file is uploaded
    if file:
        # Use an expander for file configurations
        with st.expander("File Configuration", expanded=True):
            delimiter = st.selectbox("Choose the delimiter:", [",", ";", "\t", "|", "Other"])
            if delimiter == "Other":
                delimiter = st.text_input("Specify the delimiter:", value=",")
            
            header = st.checkbox("Does the file have a header?", value=False)
        
        if header:
            data = pd.read_csv(file, delimiter=delimiter)
        else:
            data = pd.read_csv(file, delimiter=delimiter, header=None)

        st.write(data)  # Show the original dataframe

        sample_id_col = st.selectbox("Choose the 'Sample Number' column:", options=[''] + list(data.columns), key="sample_id_selectbox", index=0)
        
        # Sample Date input
        sample_date = st.date_input("Sample Date")

        if st.button("Reset Selections"):
            st.experimental_rerun()
        
        # Spacer
        st.markdown('---')    

        data_cols = [col for col in data.columns if col != sample_id_col]
        
        for i in range(0, len(data_cols), 3):
            cols = st.columns(3)
            
            for j in range(3):
                if i + j < len(data_cols):
                    col_name = data_cols[i + j]
                    cols[j].write(col_name)
                    selected_element = cols[j].selectbox("Element", options=['Select Element'] + soil_test_analysis, key=f"element_{col_name}")
                    if selected_element != 'Select Element':
                        matched_columns[col_name] = selected_element
                        if selected_element in default_units and default_units[selected_element]:
                            selected_unit = cols[j].selectbox("Unit", options=['Select Unit'] + default_units[selected_element], key=f"unit_{col_name}")
                            if selected_unit != 'Select Unit':
                                unit_columns[col_name] = selected_unit

        # Spacer
        st.markdown('---')
        
        if matched_columns:
            st.subheader("XML Output")
            xml_output = updated_generate_xml_v6(data, matched_columns, unit_columns, sample_id_col, sample_date)
            st.code(xml_output, language="xml")

            # Convert data to XML
            xml_data = convert_to_xml(data, matched_columns, unit_columns, sample_id_col, sample_date)

            # Offer download as XML
            xml_filename = "converted_data.xml"
            st.download_button(label="Download XML", data=io.BytesIO(xml_data.encode()), file_name=xml_filename, mime="text/xml")

if __name__ == "__main__":
    main()

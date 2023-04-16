import streamlit as st
from lxml import etree
from io import StringIO, BytesIO
import os

class SchemaEntityResolver(etree.Resolver):
    def resolve(self, url, pubid, context):
        if 'modus_global.xsd' in url:
            return self.resolve_filename(os.path.join('Data', 'modus_global.xsd'), context)
        elif 'modus_submit.xsd' in url:
            return self.resolve_filename(os.path.join('Data', 'modus_submit.xsd'), context)
        return self.resolve_filename(url, context)

def validate_xml(xml_data, schema_path):
    try:
        parser = etree.XMLParser(load_dtd=True, no_network=False)
        parser.resolvers.add(SchemaEntityResolver())
        schema_doc = etree.parse(schema_path, parser)
        schema = etree.XMLSchema(schema_doc)

        xml_parser = etree.XMLParser(schema=schema)
        etree.parse(BytesIO(xml_data), xml_parser)
        return True, None
    except etree.XMLSchemaError as e:
        return False, str(e)
    except etree.XMLSyntaxError as e:
        return False, str(e)

st.title("✅ Validate Modus Files")

# Upload the XML file
uploaded_file = st.file_uploader("Upload your XML file", type="xml")
if uploaded_file is not None:
    xml_data = uploaded_file.read()

    # Set the schema file path
    schema_path = os.path.join("Data", "modus_result.xsd")

    is_valid, error_message = validate_xml(xml_data, schema_path)

    if is_valid:
        st.success("The XML file is valid.")
    else:
        st.error(f"Invalid XML file. Error message: {error_message}")

        

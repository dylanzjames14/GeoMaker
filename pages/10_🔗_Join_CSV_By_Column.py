import streamlit as st
import pandas as pd
import base64

def app():
    st.title('🔗 CSV Joiner')

    # Upload first CSV
    csv1 = st.file_uploader("Upload first CSV", type=['csv'])
    if csv1 is not None:
        df1 = pd.read_csv(csv1)
        st.write(df1)

        # Select column from first CSV
        column1 = st.selectbox('Select column from first CSV', df1.columns)

    # Upload second CSV
    csv2 = st.file_uploader("Upload second CSV", type=['csv'])
    if csv2 is not None:
        df2 = pd.read_csv(csv2)
        st.write(df2)

        # Select column from second CSV
        column2 = st.selectbox('Select column from second CSV', df2.columns)

    # If both CSVs are uploaded and columns are selected
    if csv1 is not None and csv2 is not None:
        # Convert the columns to the same type before merging
        df1[column1] = df1[column1].astype(str)
        df2[column2] = df2[column2].astype(str)
        
        # Join the two dataframes
        result = pd.merge(df1, df2, left_on=column1, right_on=column2)
        st.write(result)

        # Download the result dataframe
        csv = result.to_csv(index=False)
        b64 = base64.b64encode(csv.encode()).decode()  # some strings <-> bytes conversions necessary here
        href = f'<a href="data:file/csv;base64,{b64}" download="result.csv">Download result CSV</a>'
        st.markdown(href, unsafe_allow_html=True)

if __name__ == "__main__":
    app()

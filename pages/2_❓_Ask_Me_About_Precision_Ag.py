
import streamlit as st


st.info("This app is under construction")
st.title("Ask Me About Precision Ag")
st.write("Give me a topic about precision agriculture and I will respond in 2 to 3 paragraphs as a precision ag professional.")

topic_input = st.text_input("Topic", max_chars=25,)
st.button("Go!")

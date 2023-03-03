import streamlit as st
import openai

st.warning("This is a beta free service, please limit yourself to 3 summaries per day. Inputs are the at the discretion of the user and are not being monitored.")
st.title("Ask About Ag")
st.write("This a place to help gain understanding of the agricultural industry.")

openai.api_key = st.secrets['openai']

article_text = st.text_area("Enter your agricultural topic", max_chars=30)

if st.button("Generate Summary", type='primary'):
    # Use GPT-3 to generate a summary of the article
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt="Give me a few paragraphs on the following topic as an ag professional would respond: " + article_text,
        max_tokens=4000,
        temperature=1,
    )
    # Print the generated summary
    res = response["choices"][0]["text"]
    st.success(res)
    st.download_button('Download result', res)

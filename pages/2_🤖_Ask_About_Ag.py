import streamlit as st
import openai

st.warning("This is a beta free service, please limit yourself to 3 topics per day.")
st.title("Ask About Ag")
st.write("This is a tool to help build your agricultural knowledge.")

openai.api_key = st.secrets["api_secret"]

article_text = st.text_area("Enter your agricultural topic", max_chars=30)

if st.button("Learn!"):
    # Use GPT-3 to generate a summary of the article
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt="Knowing responses must be professional. Give me a few paragraphs on the following topic as an ag professional would respond: " + article_text,
        max_tokens=4000,
        temperature=1,
    )
    # Print the generated summary
    res = response["choices"][0]["text"]
    st.success(res)
    st.download_button('Download result', res)

import streamlit as st
import openai

st.set_page_config(layout="wide")
st.title("📜 Translate")
st.write("The tool is designed to translate agricultural application text strings like a professional in the field. You can choose the language you want to translate into and input the text to be translated.")
st.warning("Information translated using this tool is being translated by OpenAI's davinci-003 model. Please be careful what you input as it is being monitored by OpenAI.")

openai.api_key = st.secrets["api_secret"]

# Create a dropdown for language selection
language_mapping = {'Spanish': 'es', 'Portuguese': 'pt', 'Afrikaans': 'af'}
language = st.selectbox("Select target language:", options=list(language_mapping.keys()))

# Create a text area for the user to input the text to be translated
input_text = st.text_area("Enter your text to be translated:", max_chars=500)

# Create a button that will trigger the translation
if st.button("Translate!"):
    with st.spinner('Translating your text...'):
        # Create a prompt for translation based on the user's input and the selected language
        prompt = f"Translate the following precision agriculture application text strings as an ag professional to {language}: '{input_text}'"

        # Call the OpenAI API to generate the translated text
        response = openai.Completion.create(
            engine="text-davinci-003",
            prompt=prompt,
            max_tokens=4000,
            temperature=1,
        )

        # Display the translated text
        translated_text = response["choices"][0]["text"].strip()
        st.success(translated_text)

        # Add a download button
        st.download_button('Download result', translated_text)


import streamlit as st
import requests
from googletrans import Translator
from indic_transliteration.sanscript import transliterate

# Function to translate and transliterate to Telugu
def translate_and_transliterate_to_telugu(text):
    translator = Translator()

    # Translate to Telugu
    translated = translator.translate(text, dest='te')
    translated_text = translated.text  # Telugu translation

    # Convert Telugu text to Romanized English (Transliteration)
    transliteration = transliterate(translated_text, 'telugu', 'iast')

    return translated_text, transliteration

# Function to correct grammar using LanguageTool API
def correct_grammar_with_languagetool_api(text):
    url = "https://api.languagetool.org/v2/check"
    params = {
        "text": text,
        "language": "en",
        "enabledOnly": "false"
    }
    
    response = requests.post(url, data=params)
    result = response.json()
    
    # Extract the corrected text
    corrected_text = text
    for match in result['matches']:
        start = match['offset']
        length = match['length']
        replacement = match['replacements'][0]['value']
        corrected_text = corrected_text[:start] + replacement + corrected_text[start+length:]
    
    return corrected_text

# Full function to process text
def process_text(text):
    # Translate and Transliterate
    translated_text, transliteration = translate_and_transliterate_to_telugu(text)
    
    # Grammar correction
    corrected_text = correct_grammar_with_languagetool_api(text)
    
    return translated_text, transliteration, corrected_text

# Streamlit UI
st.title("AI-Based Language Translator and Grammar Checker")

user_input = st.text_area("Enter your text:")

if st.button("Process Text"):
    translated_text, transliteration, corrected_text = process_text(user_input)
    
    st.write(f"Translated Text in Telugu: {translated_text}")
    st.write(f"Transliteration (in English): {transliteration}")
    st.write(f"Grammar-Corrected Text: {corrected_text}")

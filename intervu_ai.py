import streamlit as st
import openai
import pyttsx3
import speech_recognition as sr
import tempfile
import os

# Set your OpenAI API key
openai.api_key = "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"

# Function: Ask OpenAI
def ask_openai(prompt):
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a professional interview coach."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.6,
        max_tokens=500
    )
    return response.choices[0].message["content"].strip()

# Function: Text-to-Speech
def speak(text):
    engine = pyttsx3.init()
    engine.setProperty('rate', 160)
    engine.say(text)
    engine.runAndWait()

# Function: Listen to user's spoken answer
def listen():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        st.info(" Speak your answer now...")
        audio = recognizer.listen(source)
    try:
        text = recognizer.recognize_google(audio)
        st.success(f" You said: {text}")
        return text
    except sr.UnknownValueError:
        return "Sorry, I could not understand what you said."
    except sr.RequestError:
        return "Could not request results from Google Speech Recognition service."

# Streamlit UI
st.title(" Intervu.AI – Mock Interview Chatbot")
st.write(" Simulates mock interviews with OpenAI.\n Speaks questions aloud.\n Accepts spoken answers and gives feedback.")

# Select role
role = st.text_input("Enter the job role you're applying for (e.g., Data Analyst, Product Manager):")

if st.button("Start Interview"):
    if role:
        with st.spinner("Generating interview question..."):
            question = ask_openai(f"Give me one realistic mock interview question for the role of {role}.")
        st.subheader(" Interviewer:")
        st.write(question)
        speak(question)

        answer = listen()

        with st.spinner("Analyzing your answer..."):
            feedback_prompt = f"Here is the question: {question}\nAnd here is the candidate's answer: {answer}\nGive detailed professional feedback."
            feedback = ask_openai(feedback_prompt)

        st.subheader(" Interview Coach Feedback:")
        st.write(feedback)
        speak("Here is your feedback.")
        speak(feedback)
    else:
        st.warning("Please enter a job role to begin.")

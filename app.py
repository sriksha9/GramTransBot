import streamlit as st
import openai
import os

# Setup your OpenAI API key from Streamlit secrets (for deployment)
openai.api_key = os.getenv("OPENAI_API_KEY")

# Title
st.set_page_config(page_title="Interview Prep Chatbot", layout="centered")
st.title("🎤 Interview Prep Chatbot")
st.markdown("Simulate mock interviews and get real-time feedback on your answers.")

# Roles and question types
roles = ["Data Analyst", "Product Manager", "Software Engineer", "Business Analyst"]
types = ["HR", "Technical", "Behavioral"]

# Sidebar selections
role = st.selectbox("👤 Select a job role", roles)
interview_type = st.radio("📋 Select interview type", types)

# Generate question
if st.button("🎯 Generate Interview Question"):
    prompt = f"Give one {interview_type} interview question for a {role}."
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a professional interview coach."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=100
        )
        question = response['choices'][0]['message']['content'].strip()
        st.session_state["question"] = question
        st.success("Question generated!")
        st.markdown(f"** Interviewer:** {question}")
    except Exception as e:
        st.error(f"Error: {e}")

# User answer input
if "question" in st.session_state:
    user_answer = st.text_area(" Your Answer", placeholder="Type your answer here...")
    if st.button(" Get Feedback"):
        if user_answer.strip() == "":
            st.warning("Please enter your answer before submitting.")
        else:
            feedback_prompt = f"""
            As a skilled interview coach, give feedback on the following response:
            Question: {st.session_state['question']}
            Answer: {user_answer}
            Provide improvements, structure, and a score out of 10.
            """
            try:
                feedback_response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "user", "content": feedback_prompt}
                    ],
                    temperature=0.7,
                    max_tokens=500
                )
                feedback = feedback_response['choices'][0]['message']['content'].strip()
                st.subheader(" Feedback")
                st.markdown(feedback)
            except Exception as e:
                st.error(f"Error generating feedback: {e}")

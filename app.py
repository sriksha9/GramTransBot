import streamlit as st
import os
from openai import OpenAI

# Load the OpenAI API key securely from Streamlit secrets
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

st.set_page_config(page_title="Interview Prep Chatbot", layout="centered")
st.title("Interview Prep Chatbot")
st.write("Enter a job role and simulate mock interviews with feedback.")

# User types the job role
job_role = st.text_input("Enter the Job Role (e.g., Data Analyst, Software Engineer, etc.)")

# Interview type selection
interview_type = st.radio("Select the Interview Type", ["HR", "Technical", "Behavioral"])

# Generate question
if st.button("Generate Interview Question"):
    if not job_role.strip():
        st.warning("Please enter a job role.")
    else:
        try:
            prompt = f"Generate one {interview_type} interview question for a {job_role}."
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a professional interview coach."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=200
            )
            question = response.choices[0].message.content.strip()
            st.session_state["question"] = question
            st.success("Question Generated")
            st.markdown(f"**Interviewer:** {question}")
        except Exception as e:
            st.error(f"OpenAI Error: {e}")

# User types their answer
if "question" in st.session_state:
    user_answer = st.text_area("Your Answer", placeholder="Type your answer here...")

    if st.button("Get Feedback"):
        if not user_answer.strip():
            st.warning("Please type an answer first.")
        else:
            try:
                feedback_prompt = (
                    f"As a skilled interview coach, give feedback on this answer:\n"
                    f"Question: {st.session_state['question']}\n"
                    f"Answer: {user_answer}\n"
                    f"Provide strengths, improvements, and a rating out of 10."
                )
                feedback_response = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "user", "content": feedback_prompt}
                    ],
                    temperature=0.7,
                    max_tokens=500
                )
                feedback = feedback_response.choices[0].message.content.strip()
                st.subheader("Feedback")
                st.write(feedback)
            except Exception as e:
                st.error(f"OpenAI Error: {e}")

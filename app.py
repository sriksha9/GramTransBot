import streamlit as st
import os
from openai import OpenAI

# Load OpenAI API key from Streamlit Secrets
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

st.set_page_config(page_title="Interview Prep Chatbot", layout="centered")
st.title("Interview Prep Chatbot")
st.write("Practice interview questions and chat with a professional interview coach.")

# Input: Job Role and Interview Type
job_role = st.text_input("Enter the Job Role (e.g., Data Analyst, Software Engineer)")
interview_type = st.radio("Select the Interview Type", ["HR", "Technical", "Behavioral"])

# Generate a Question
if st.button("Generate Interview Question"):
    if not job_role.strip():
        st.warning("Please enter a job role.")
    else:
        try:
            prompt = f"Generate one {interview_type} interview question for a {job_role}."
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful mock interview coach."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=200
            )
            question = response.choices[0].message.content.strip()
            st.session_state["question"] = question
            st.success("Interview Question Generated")
            st.markdown(f"**Interviewer:** {question}")
        except Exception as e:
            st.error(f"OpenAI Error: {e}")

# User provides answer
if "question" in st.session_state:
    user_answer = st.text_area("Your Answer", placeholder="Type your response here...")

    if st.button("Get Feedback"):
        if not user_answer.strip():
            st.warning("Please enter your answer.")
        else:
            try:
                feedback_prompt = (
                    f"As an interview coach, provide feedback on this answer:\n"
                    f"Question: {st.session_state['question']}\n"
                    f"Answer: {user_answer}\n"
                    f"Provide feedback with strengths, improvements, and a score out of 10."
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
                st.session_state["chat_ready"] = True  # Enable chat after feedback
            except Exception as e:
                st.error(f"OpenAI Error: {e}")



if st.session_state.get("chat_ready", False):
    st.subheader("Ask the Interview Coach (Tips, Advice, Guidance)")
    if "chat_history" not in st.session_state:
        st.session_state["chat_history"] = [
            {"role": "system", "content": "You are a supportive and experienced interview coach."}
        ]

    user_chat_input = st.text_input("Ask a follow-up question (e.g., 'How can I stay calm in an interview?')")

    if st.button("Ask Coach"):
        if user_chat_input:
            st.session_state["chat_history"].append({"role": "user", "content": user_chat_input})
            try:
                chat_response = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=st.session_state["chat_history"],
                    temperature=0.7,
                    max_tokens=300
                )
                reply = chat_response.choices[0].message.content.strip()
                st.session_state["chat_history"].append({"role": "assistant", "content": reply})
                st.markdown(f"**Coach:** {reply}")
            except Exception as e:
                st.error(f"OpenAI Error: {e}")

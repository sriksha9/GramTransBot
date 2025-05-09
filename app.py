import streamlit as st
import os
from openai import OpenAI
import datetime
import re
import pandas as pd
import altair as alt

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

st.set_page_config(page_title="IntervuBot - Interview Coach", layout="centered")
st.title("IntervuBot - Interview Coach")
st.write("Practice interviews, get feedback, and track your improvement.")

# Initialize session state
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "score_log" not in st.session_state:
    st.session_state.score_log = []

# Input fields
job_role = st.text_input("Enter the Job Role")
interview_type = st.radio("Select Interview Type", ["HR", "Technical", "Behavioral"])
ai_coach_mode = st.checkbox("Enable AI-Coach Mode")

# Generate question
if st.button("Generate Interview Question"):
    if job_role.strip():
        prompt = f"Generate one {interview_type} interview question for a {job_role}."
        try:
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a professional interview coach."},
                    {"role": "user", "content": prompt}
                ]
            )
            question = response.choices[0].message.content.strip()
            st.session_state.chat_history.append({"role": "assistant", "content": f"Interviewer: {question}"})
            st.success("Question Generated")

            # Optional AI-Coach Advice
            if ai_coach_mode:
                coach_prompt = f"Give advice to answer this question effectively: {question}"
                advice_response = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "user", "content": coach_prompt}]
                )
                advice = advice_response.choices[0].message.content.strip()
                st.session_state.chat_history.append({"role": "assistant", "content": f"AI Coach Advice: {advice}"})

            st.session_state.chat_history.append({"role": "system", "content": f"Question: {question}"})
        except Exception as e:
            st.error(f"OpenAI Error: {e}")
    else:
        st.warning("Please enter a job role.")

# Chat interface
user_input = st.chat_input("Your answer or question")
if user_input:
    st.session_state.chat_history.append({"role": "user", "content": user_input})
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": msg["role"], "content": msg["content"]} for msg in st.session_state.chat_history],
            temperature=0.7,
            max_tokens=500
        )
        reply = response.choices[0].message.content.strip()
        st.session_state.chat_history.append({"role": "assistant", "content": reply})

        # Attempt to extract score if mentioned
        score_match = re.search(r"([Ss]core|rating)\D*(\d{1,2})/10", reply)
        if score_match:
            score = int(score_match.group(2))
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
            st.session_state.score_log.append({"timestamp": timestamp, "score": score})

    except Exception as e:
        st.error(f"OpenAI Error: {e}")

# Display chat history
st.subheader("Conversation")
for msg in st.session_state.chat_history:
    if msg["role"] == "user":
        st.markdown(f"👤 You: {msg['content']}")
    elif msg["role"] == "assistant":
        st.markdown(f"🧠 Bot: {msg['content']}")

# Score dashboard
if st.session_state.score_log:
    st.subheader("Score History")
    df = pd.DataFrame(st.session_state.score_log)
    chart = alt.Chart(df).mark_line(point=True).encode(
        x='timestamp:T',
        y='score:Q'
    ).properties(height=300)
    st.altair_chart(chart, use_container_width=True)

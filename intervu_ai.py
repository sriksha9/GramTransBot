import streamlit as st
from streamlit_webrtc import webrtc_streamer, AudioProcessorBase
import numpy as np
import soundfile as sf
import av
import uuid
import os
from openai import OpenAI
import tempfile

#  Securely load OpenAI key from environment (set in Streamlit Secrets)
client = OpenAI(api_key=st.secrets["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"])

# App setup
st.set_page_config(page_title="Intervu.AI", layout="centered")
st.title(" Intervu.AI – Mock Interview Chatbot")

st.markdown("""
Prepare for interviews interactively:
1.  Enter a job role  
2.  Get an AI-generated interview question  
3.  Speak your answer  
4.  Receive detailed feedback
""")

# Step 1: Get role input
role = st.text_input("Enter a job role (e.g., Data Analyst, Product Manager):")

if st.button("Get Interview Question"):
    if not role.strip():
        st.warning("Please enter a job role.")
    else:
        with st.spinner("Generating interview question..."):
            response = client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "user", "content": f"Generate a realistic interview question for the role: {role}"}
                ]
            )
            question = response.choices[0].message.content.strip()
            st.session_state["question"] = question
            st.success("Generated Question:")
            st.write(f" Interviewer: {question}")

# Step 2: Audio recording using WebRTC
if "question" in st.session_state:
    st.markdown(" Please record your answer below:")

    class AudioProcessor(AudioProcessorBase):
        def __init__(self):
            self.frames = []

        def recv(self, frame: av.AudioFrame) -> av.AudioFrame:
            audio = frame.to_ndarray().flatten()
            self.frames.append(audio)
            return frame

    ctx = webrtc_streamer(
        key="audio-recorder",
        mode="sendonly",
        audio_receiver_size=1024,
        audio_processor_factory=AudioProcessor,
        media_stream_constraints={"audio": True, "video": False},
    )

    if ctx.audio_processor:
        if st.button("Submit Answer"):
            st.info("Processing your response...")

            # Save audio to a temporary file
            audio_data = np.concatenate(ctx.audio_processor.frames).astype(np.int16)
            temp_filename = f"{uuid.uuid4().hex}.wav"
            sf.write(temp_filename, audio_data, 48000)

            # Step 3: Transcribe with Whisper
            with open(temp_filename, "rb") as f:
                transcript = client.audio.transcriptions.create(
                    model="whisper-1",
                    file=f
                ).text

            st.subheader(" Your Transcribed Answer:")
            st.write(transcript)

            # Step 4: Generate Feedback
            with st.spinner("Analyzing answer..."):
                feedback_prompt = f"""
You are an AI interview coach. The candidate was asked:

"{st.session_state['question']}"

They answered:

"{transcript}"

Provide structured, ATS-friendly feedback with strengths, weaknesses, and improvement suggestions.
"""
                feedback_response = client.chat.completions.create(
                    model="gpt-4",
                    messages=[
                        {"role": "user", "content": feedback_prompt}
                    ],
                    temperature=0.6,
                    max_tokens=500
                )
                feedback = feedback_response.choices[0].message.content.strip()

            st.subheader(" AI Feedback:")
            st.write(feedback)

            os.remove(temp_filename)

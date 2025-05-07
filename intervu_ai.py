import streamlit as st
from streamlit_webrtc import webrtc_streamer, AudioProcessorBase
import numpy as np
import tempfile
import av
import os
import uuid
import soundfile as sf
from openai import OpenAI

#  Set your OpenAI key
client = OpenAI(api_key="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")

st.set_page_config(page_title="Intervu.AI", layout="centered")
st.title(" Intervu.AI – Mock Interview Chatbot")
st.markdown("""
Prepare for interviews interactively:
1.  Enter a job role  
2.  Get an AI-generated interview question  
3. 🎙peak your answer  
4.  Receive detailed feedback
""")

# Step 1: Get user-selected job role
role = st.text_input("Enter job role (e.g., Data Analyst, Software Engineer):")

if st.button("Get Interview Question"):
    if not role.strip():
        st.warning("Please enter a job role to proceed.")
    else:
        with st.spinner("Generating question..."):
            response = client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "user", "content": f"Generate a realistic and challenging interview question for a {role}."}
                ]
            )
            question = response.choices[0].message.content.strip()
            st.session_state["question"] = question
            st.success("Question generated:")
            st.write(f" Interviewer: {question}")

# Step 2: Record user's audio answer
if "question" in st.session_state:
    st.markdown("🎙 Speak your answer below:")

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
            st.info("Processing your answer. Please wait...")

            # Save recording to temp WAV file
            audio_data = np.concatenate(ctx.audio_processor.frames).astype(np.int16)
            temp_filename = f"{uuid.uuid4().hex}.wav"
            sf.write(temp_filename, audio_data, 48000)

            with open(temp_filename, "rb") as f:
                transcript = client.audio.transcriptions.create(
                    model="whisper-1",
                    file=f
                ).text

            st.subheader(" Transcription of Your Answer:")
            st.write(transcript)

            # Get interview feedback
            with st.spinner("Analyzing answer..."):
                feedback_response = client.chat.completions.create(
                    model="gpt-4",
                    messages=[
                        {
                            "role": "user",
                            "content": f"""
You are an AI interview coach. A candidate was asked the following interview question:

"{st.session_state['question']}"

They answered:

"{transcript}"

Provide structured feedback including strengths, weaknesses, and tips for improvement.
"""
                        }
                    ],
                    temperature=0.6,
                    max_tokens=500
                )
                feedback = feedback_response.choices[0].message.content.strip()

            st.subheader(" AI Feedback:")
            st.write(feedback)

            os.remove(temp_filename)

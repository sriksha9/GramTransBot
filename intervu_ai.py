import streamlit as st
from streamlit_webrtc import webrtc_streamer, AudioProcessorBase
import openai
import numpy as np
import tempfile
import av
import os
import uuid
import base64
import time

# Set your OpenAI key here or use secrets in production
openai.api_key = "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"

# Title and instructions
st.title(" Intervu.AI – Mock Interview Chatbot")
st.markdown("""
🔹 Enter a job role  
🔹 Click "Get Interview Question"  
🔹 Answer it with your voice  
🔹 Get real-time feedback  
""")

# Step 1: Get job role
role = st.text_input("Enter job role (e.g., Data Analyst, Software Engineer):")

if st.button("Get Interview Question"):
    if not role.strip():
        st.warning("Please enter a role first.")
    else:
        with st.spinner("Generating interview question..."):
            question_prompt = f"Generate a realistic interview question for the role of {role}."
            question = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[{"role": "user", "content": question_prompt}]
            ).choices[0].message["content"].strip()
        st.session_state["question"] = question
        st.success("Question generated!")
        st.write(f" Interviewer: {question}")

# Step 2: Record user's voice response
if "question" in st.session_state:
    st.markdown(" Speak your answer below:")

    class AudioProcessor(AudioProcessorBase):
        def __init__(self):
            self.recorded_frames = []

        def recv(self, frame: av.AudioFrame) -> av.AudioFrame:
            audio = frame.to_ndarray().flatten()
            self.recorded_frames.append(audio)
            return frame

    ctx = webrtc_streamer(
        key="speech",
        mode="sendonly",
        audio_receiver_size=1024,
        audio_processor_factory=AudioProcessor,
        media_stream_constraints={"audio": True, "video": False},
    )

    if ctx.audio_processor:
        if st.button("Submit Answer"):
            st.info("Processing your answer, please wait...")

            # Combine audio frames
            audio_np = np.concatenate(ctx.audio_processor.recorded_frames, axis=0).astype(np.int16)
            temp_wav_path = f"{uuid.uuid4().hex}.wav"

            # Save as temp WAV file
            import soundfile as sf
            sf.write(temp_wav_path, audio_np, 48000)

            # Transcribe with Whisper
            with open(temp_wav_path, "rb") as f:
                transcript = openai.Audio.transcribe("whisper-1", f)["text"]

            st.subheader(" You said:")
            st.write(transcript)

            # Feedback from GPT
            with st.spinner("Getting feedback from AI coach..."):
                feedback_prompt = f"""You're an interview coach.
Question: {st.session_state['question']}
Candidate Answer: {transcript}
Give detailed feedback on strengths, weaknesses, and improvement suggestions."""
                feedback = openai.ChatCompletion.create(
                    model="gpt-4",
                    messages=[{"role": "user", "content": feedback_prompt}],
                    temperature=0.6,
                    max_tokens=500
                ).choices[0].message["content"].strip()

            st.subheader(" Interview Feedback:")
            st.write(feedback)

            os.remove(temp_wav_path)

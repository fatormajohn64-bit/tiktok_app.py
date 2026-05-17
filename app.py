import streamlit as st
import os
import random
import json
from datetime import datetime
from groq import Groq
from gtts import gTTS

from moviepy.editor import (
    VideoFileClip,
    AudioFileClip,
    CompositeAudioClip,
)

# =========================
# PAGE CONFIG
# =========================

st.set_page_config(
    page_title="Islamic Video Factory Ultimate",
    layout="wide"
)

# =========================
# STYLES
# =========================

st.markdown("""
<style>
.main {
    background: linear-gradient(135deg,#031b14,#064e3b);
    color: white;
}
.stButton>button {
    background: #10b981;
    color: white;
    border-radius: 12px;
    border: none;
    padding: 12px 20px;
    font-size: 18px;
    font-weight: bold;
}
.memory-box {
    background: rgba(255,255,255,0.08);
    padding: 15px;
    border-radius: 15px;
    margin-top: 10px;
}
</style>
""", unsafe_allow_html=True)

# =========================
# TITLE
# =========================

st.title("☪ Islamic Video Factory Ultimate")
st.write("Generate cinematic Islamic AI videos with Groq + MoviePy")

# =========================
# GROQ API
# =========================

try:
    GROQ_API_KEY = st.secrets["GROQ_API_KEY"]

    client = Groq(
        api_key=GROQ_API_KEY
    )

    st.success("✅ Groq API Connected")

except Exception as e:
    st.error(f"Groq Error: {e}")
    st.stop()

# =========================
# MEMORY SYSTEM
# =========================

MEMORY_FILE = "memory.json"

if not os.path.exists(MEMORY_FILE):
    with open(MEMORY_FILE, "w") as f:
        json.dump([], f)

def save_memory(topic, script):
    with open(MEMORY_FILE, "r") as f:
        data = json.load(f)

    data.append({
        "topic": topic,
        "script": script,
        "time": str(datetime.now())
    })

    with open(MEMORY_FILE, "w") as f:
        json.dump(data, f, indent=2)

def load_memory():
    with open(MEMORY_FILE, "r") as f:
        return json.load(f)

# =========================
# VIDEO TOPIC
# =========================

topic = st.text_input(
    "Video Topic",
    "Motivation"
)

# =========================
# GENERATE BUTTON
# =========================

if st.button("Generate Cinematic Islamic Video"):

    try:

        st.info("🎬 Generating AI cinematic video...")

        # =========================
        # STEP 1 — SCRIPT
        # =========================

        st.write("Step 1: Compiling narration via Groq...")

        prompt = f"""
        Create a powerful cinematic Islamic motivational narration about:
        {topic}

        Make it emotional, deep, inspiring, spiritual,
        short-form TikTok style,
        and suitable for cinematic voice narration.
        """

        response = client.chat.completions.create(
            model="llama3-8b-8192",
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=1,
            max_tokens=500,
        )

        script = response.choices[0].message.content

        st.success("Narration Generated")
        st.write(script)

        # =========================
        # SAVE MEMORY
        # =========================

        save_memory(topic, script)

        # =========================
        # STEP 2 — VOICE
        # =========================

        st.write("Step 2: Generating voice narration...")

        tts = gTTS(script)

        audio_path = "voice.mp3"

        tts.save(audio_path)

        # =========================
        # STEP 3 — VIDEO
        # =========================

        st.write("Step 3: Processing cinematic visuals...")

        background_video = "background.mp4"

        if not os.path.exists(background_video):
            st.error("background.mp4 not found")
            st.stop()

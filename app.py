# =========================================================
# ISLAMIC VIDEO CONTENT FACTORY PRO
# GROQ + LLAMA 3.3 70B + STREAMLIT + MOVIEPY
# =========================================================

import os
import json
import time
import hashlib
import tempfile
import streamlit as st
import imageio_ffmpeg

from groq import Groq
from gtts import gTTS

from moviepy.editor import (
    VideoFileClip,
    AudioFileClip,
    CompositeVideoClip,
    ColorClip
)

# =========================================================
# FFMPEG FIX
# =========================================================

os.environ["IMAGEIO_FFMPEG_EXE"] = imageio_ffmpeg.get_ffmpeg_exe()

# =========================================================
# STREAMLIT PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="Islamic Video Content Factory PRO",
    layout="wide"
)

# =========================================================
# CUSTOM UI
# =========================================================

st.markdown("""
<style>

.stApp {
    background-color: #06110b;
    color: white;
}

h1, h2, h3 {
    color: #00d084;
}

.stButton>button {
    background-color: #00d084;
    color: black;
    border-radius: 12px;
    font-weight: bold;
}

section[data-testid="stSidebar"] {
    background-color: #08140d;
}

</style>
""", unsafe_allow_html=True)

# =========================================================
# TITLE
# =========================================================

st.title("☪ Islamic Video Content Factory PRO")

st.write(
    "Generate cinematic Islamic AI videos powered by Groq + Llama 3.3 70B."
)

# =========================================================
# GROQ API SETUP
# =========================================================

try:

    GROQ_API_KEY = st.secrets["GROQ_API_KEY"]

    client = Groq(
        api_key=GROQ_API_KEY
    )

    st.success("Groq API Connected Successfully")

except Exception as e:

    st.error(f"Groq Connection Failed: {e}")
    st.stop()

# =========================================================
# MASSIVE MEMORY SYSTEM
# =========================================================

MEMORY_FILE = "memory.json"

DEFAULT_MEMORY = {
    "used_hashes": [],
    "used_topics": []
}

if not os.path.exists(MEMORY_FILE):

    with open(MEMORY_FILE, "w") as f:

        json.dump(DEFAULT_MEMORY, f)

def load_memory():

    with open(MEMORY_FILE, "r") as f:

        return json.load(f)

def save_memory(data):

    with open(MEMORY_FILE, "w") as f:

        json.dump(data, f, indent=2)

memory = load_memory()

# =========================================================
# SIDEBAR CONTROLS
# =========================================================

st.sidebar.title("Video Settings")

video_format = st.sidebar.selectbox(
    "Video Format",
    [
        "TikTok / Shorts / Reels",
        "YouTube Long-form"
    ]
)

length_option = st.sidebar.selectbox(
    "Target Video Length",
    [
        "30 Seconds",
        "1 Minute",
        "2 Minutes",
        "5 Minutes",
        "10 Minutes"
    ]
)

theme = st.sidebar.selectbox(
    "Content Theme",
    [
        "Motivational Reminder",
        "Historical Story / Seerah",
        "Quranic Reflection",
        "Daily Duas & Supplications",
        "Heart-Trembling Recitation Context"
    ]
)

topic = st.sidebar.text_input(
    "Video Topic",
    placeholder="Example: Tawakkul in Islam"
)

# =========================================================
# VIDEO DIMENSIONS
# =========================================================

if video_format == "TikTok / Shorts / Reels":

    VIDEO_WIDTH = 720
    VIDEO_HEIGHT = 1280

else:

    VIDEO_WIDTH = 1280
    VIDEO_HEIGHT = 720

# =========================================================
# VIDEO DURATION MAP
# =========================================================

duration_map = {

    "30 Seconds": 30,
    "1 Minute": 60,
    "2 Minutes": 120,
    "5 Minutes": 300,
    "10 Minutes": 600

}

TARGET_DURATION = duration_map[length_option]

# =========================================================
# SYSTEM PROMPT
# =========================================================

SYSTEM_PROMPT = f"""

You are an elite Islamic scholar, historian,
cinematic storyteller, and motivational speaker.

You possess deep knowledge of:

- Quran Tafsir
- Authentic Hadith
- Sahih Bukhari
- Sahih Muslim
- Islamic Seerah
- Islamic Golden Age
- Companions of the Prophet
- Spiritual purification
- Emotional Islamic reminders

CRITICAL RULES:

- NEVER repeat scripts
- NEVER reuse standard hooks
- NEVER duplicate paragraphs
- Use highly diverse vocabulary
- Use different storytelling structures
- Use emotional cinematic pacing
- Generate highly unique content every time

STRICT OUTPUT RULE:

Return ONLY direct spoken narration text.

DO NOT include:
- Scene numbers
- Director notes
- Bullet points
- Labels
- Brackets
- Captions

Write naturally for text-to-speech narration.

"""

# =========================================================
# SCRIPT GENERATION
# =========================================================

def generate_script():

    user_prompt = f"""

    Topic:
    {topic}

    Theme:
    {theme}

    Video Length:
    {length_option}

    Requirements:

    - Emotional narration
    - Cinematic storytelling
    - Authentic Islamic wisdom
    - Viral social media pacing
    - Powerful hooks
    - Deep reflections

    Avoid repeating:
    {memory['used_topics'][-100:]}

    """

    response = client.chat.completions.create(

        model="llama-3.3-70b-versatile",

        messages=[

            {
                "role": "system",
                "content": SYSTEM_PROMPT
            },

            {
                "role": "user",
                "content": user_prompt
            }

        ],

        temperature=1.1,
        max_tokens=4000

    )

    return response.choices[0].message.content

# =========================================================
# HASH SYSTEM
# =========================================================

def save_hash(text):

    h = hashlib.md5(
        text.encode()
    ).hexdigest()

    memory["used_hashes"].append(h)

    save_memory(memory)

# =========================================================
# TEXT TO SPEECH
# =========================================================

def create_voiceover(script_text):

    with tempfile.NamedTemporaryFile(
        suffix=".mp3",
        delete=False,
        dir="/tmp"
    ) as temp_audio:

        audio_path = temp_audio.name

    tts = gTTS(
        text=script_text,
        lang="en"
    )

    tts.save(audio_path)

    return audio_path

# =========================================================
# VIDEO CREATION
# =========================================================

def create_video(audio_path):

    with tempfile.NamedTemporaryFile(
        suffix=".mp4",
        delete=False,
        dir="/tmp"
    ) as temp_video:

        output_path = temp_video.name

    audio_clip = AudioFileClip(audio_path)

    # -----------------------------------------------------
    # BACKGROUND VIDEO
    # -----------------------------------------------------

    if os.path.exists("background.mp4"):

        try:

            background = VideoFileClip(
                "background.mp4"
            ).subclip(0, TARGET_DURATION)

        except:

            background = None

    else:

        background = None

    # -----------------------------------------------------
    # FALLBACK COLOR SYSTEM
    # -----------------------------------------------------

    if background is None:

        if theme == "Historical Story / Seerah":

            bg_color = (15, 10, 30)

        elif theme == "Quranic Reflection":

            bg_color = (5, 40, 25)

        else:

            bg_color = (5, 25, 15)

        background = ColorClip(

            size=(VIDEO_WIDTH, VIDEO_HEIGHT),

            color=bg_color,

            duration=TARGET_DURATION

        )

    # -----------------------------------------------------
    # COMBINE AUDIO + VIDEO
    # -----------------------------------------------------

    final_video = CompositeVideoClip([
        background
    ])

    final_video = final_video.set_audio(audio_clip)

    # -----------------------------------------------------
    # EXPORT
    # -----------------------------------------------------

    final_video.write_videofile(

        output_path,

        fps=24,

        codec="libx264",

        audio_codec="aac",

        bitrate="5000k"

    )

    return output_path

# =========================================================
# DOWNLOAD SCRIPT
# =========================================================

def script_download(script):

    return script.encode("utf-8")

# =========================================================
# GENERATE BUTTON
# =========================================================

if st.button("Generate Islamic Cinematic Video"):

    try:

        with st.status(
            "Generating Islamic AI Content...",
            expanded=True
        ) as status:

            # -------------------------------------------------
            # STEP 1
            # -------------------------------------------------

            st.write("Generating narration script...")

            script = generate_script()

            save_hash(script)

            memory["used_topics"].append(topic)

            save_memory(memory)

            # -------------------------------------------------
            # STEP 2
            # -------------------------------------------------

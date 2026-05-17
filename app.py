import streamlit as st
import os
import json
import tempfile
import uuid
from datetime import datetime

from groq import Groq
from gtts import gTTS

from moviepy.editor import (
    AudioFileClip,
    VideoFileClip,
    ImageClip,
    ColorClip,
    concatenate_videoclips,
    concatenate_audioclips,
    CompositeVideoClip
)

from PIL import Image, ImageDraw, ImageFont

import numpy as np

# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="Islamic Video Factory Ultimate",
    page_icon="☪",
    layout="wide"
)

# =========================================================
# CUSTOM CSS
# =========================================================

st.markdown(
    """
    <style>
    .stApp {
        background-color: #03140c;
        color: white;
    }

    h1, h2, h3 {
        color: #00ff9d;
    }

    .stButton>button {
        background-color: #00aa66;
        color: white;
        border-radius: 10px;
        font-weight: bold;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# =========================================================
# SIDEBAR
# =========================================================

st.sidebar.title("⚙ Video Controls")

video_format = st.sidebar.selectbox(
    "Video Format",
    [
        "TikTok / Shorts / Reels",
        "YouTube Long-form"
    ]
)

video_length = st.sidebar.selectbox(
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

# =========================================================
# VIDEO SIZE
# =========================================================

if video_format == "TikTok / Shorts / Reels":
    VIDEO_WIDTH = 720
    VIDEO_HEIGHT = 1280
else:
    VIDEO_WIDTH = 1280
    VIDEO_HEIGHT = 720

# =========================================================
# DURATION MAP
# =========================================================

DURATION_MAP = {
    "30 Seconds": 30,
    "1 Minute": 60,
    "2 Minutes": 120,
    "5 Minutes": 300,
    "10 Minutes": 600
}

TARGET_DURATION = DURATION_MAP[video_length]

# =========================================================
# MEMORY SYSTEM
# =========================================================

MEMORY_FILE = "memory.json"

if not os.path.exists(MEMORY_FILE):
    with open(MEMORY_FILE, "w") as f:
        json.dump([], f)


def load_memory():
    with open(MEMORY_FILE, "r") as f:
        return json.load(f)


def save_memory(topic):
    memory = load_memory()
    memory.append(topic)

    memory = memory[-500:]

    with open(MEMORY_FILE, "w") as f:
        json.dump(memory, f)


used_topics = load_memory()

# =========================================================
# TITLE
# =========================================================

st.title("☪ Islamic Video Factory Ultimate")

st.write(
    "Generate professional cinematic Islamic AI videos using Groq + Llama 3.3 70B."
)

# =========================================================
# API KEY
# =========================================================

try:
    GROQ_API_KEY = st.secrets["GROQ_API_KEY"]

    client = Groq(
        api_key=GROQ_API_KEY
    )

    st.success("✅ Groq API Connected")

except Exception as e:

    st.error(f"Groq API Error: {e}")

    st.stop()

# =========================================================
# USER INPUT
# =========================================================

video_topic = st.text_input(
    "Video Topic",
    placeholder="Example: Patience During Hardship"
)

# =========================================================
# SCRIPT GENERATION
# =========================================================

SYSTEM_PROMPT = f"""
You are an elite Islamic scholar, cinematic narrator, documentary writer,
and emotional motivational storyteller.

Your knowledge includes:
- Quran
- Tafsir
- Authentic Hadith
- Seerah
- Islamic history
- Companions
- Islamic Golden Age
- Emotional reminders
- Motivational Islamic speeches

STRICT RULES:
- Never repeat previous structures.
- Always use fresh vocabulary.
- Always create unique emotional hooks.
- Never recycle openings.
- Create cinematic narration.
- Return ONLY narration text.
- No scene labels.
- No markdown.
- No bullet points.
- No numbering.
- No brackets.

Previously used topics:
{used_topics}

The narration should fit approximately {TARGET_DURATION} seconds.
"""

# =========================================================
# AI SCRIPT FUNCTION
# =========================================================

@st.cache_data(show_spinner=False)
def generate_script(topic, theme_name):

    completion = client.chat.completions.create(

        model="llama-3.3-70b-versatile",

        messages=[
            {
                "role": "system",
                "content": SYSTEM_PROMPT
            },
            {
                "role": "user",
                "content": f"Create a cinematic Islamic narration about {topic} under the theme {theme_name}."
            }
        ],

        temperature=1.1,
        max_tokens=3000
    )

    return completion.choices[0].message.content

# =========================================================
# TTS
# =========================================================


def generate_voice(script_text):

    tts = gTTS(
        text=script_text,
        lang="en"
    )

    audio_path = f"/tmp/{uuid.uuid4()}.mp3"

    tts.save(audio_path)

    return audio_path

# =========================================================
# CREATE SUBTITLE IMAGE
# =========================================================


def create_subtitle_image(text, width, height):

    image = Image.new(
        "RGBA",
        (width, height),
        (0, 0, 0, 0)
    )

    draw = ImageDraw.Draw(image)

    try:
        font = ImageFont.truetype("arial.ttf", 42)
    except:
        font = ImageFont.load_default()

    wrapped = text[:120]

    draw.text(
        (40, height - 220),
        wrapped,
        font=font,
        fill="white"
    )

    return np.array(image)

# =========================================================
# VIDEO CREATION
# =========================================================


def create_video(audio_path, narration_text):

    audio_clip = AudioFileClip(audio_path)

    duration = audio_clip.duration

    background = None

    # =====================================================
    # REAL BACKGROUND VIDEO
    # =====================================================

    if os.path.exists("background.mp4"):

        try:

            bg_video = VideoFileClip("background.mp4")

            if bg_video.duration < duration:

                loops_needed = int(duration // bg_video.duration) + 1

                clips = []

                for _ in range(loops_needed):
                    clips.append(bg_video.copy())

                background = concatenate_videoclips(clips)

            else:
                background = bg_video

            background = background.subclip(0, duration)

        except Exception as e:

            st.warning(f"Background video failed: {e}")

            background = None

    # =====================================================
    # FALLBACK CINEMATIC COLORS
    # =====================================================

    if background is None:

        if theme == "Historical Story / Seerah":
            color = (10, 10, 25)

        elif theme == "Quranic Reflection":
            color = (5, 35, 20)

        else:
            color = (0, 25, 15)

        background = ColorClip(
            size=(VIDEO_WIDTH, VIDEO_HEIGHT),
            color=color,
            duration=duration
        )

    background = background.resize(
        (VIDEO_WIDTH, VIDEO_HEIGHT)
    )

    # =====================================================
    # SUBTITLE OVERLAY
    # =====================================================

    subtitle_array = create_subtitle_image(
        narration_text,
        VIDEO_WIDTH,
        VIDEO_HEIGHT
    )

    subtitle_clip = ImageClip(subtitle_array)

    subtitle_clip = subtitle_clip.set_duration(duration)

    final = CompositeVideoClip([
        background,
        subtitle_clip
    ])

    final = final.set_audio(audio_clip)

    # =====================================================
    # OUTPUT
    # =====================================================

    output_path = f"/tmp/{uuid.uuid4()}.mp4"

    final.write_videofile(

        output_path,

        fps=24,

        codec="libx264",

        audio_codec="aac",

        preset="medium",

        bitrate="5000k",

        ffmpeg_params=[
            "-pix_fmt", "yuv420p"
        ],

        temp_audiofile="/tmp/temp-audio.m4a",

        remove_temp=True,

        logger=None
    )

    return output_path

# =========================================================
# MAIN BUTTON
# =========================================================

if st.button("Generate Cinematic Islamic Video"):

    if not video_topic:
        st.warning("Please enter a topic.")
        st.stop()

    try:

        with st.status("Generating AI cinematic video...", expanded=True) as status:

            st.write("Step 1: Compiling narration via Groq...")

            script = generate_script(
                video_topic,
                theme
            )

            st.write("Step 2: Generating voice narration...")

            audio_file = generate_voice(script)

            st.write("Step 3: Processing cinematic visuals...")

            video_file = create_video(
                audio_file,
                script
            )

            status.update(
                label="Video generation completed.",
                state="complete"
            )

        # =================================================
        # SAVE MEMORY
        # =================================================

        save_memory(video_topic)

        # =================================================
        # DISPLAY SCRIPT
        # =================================================

        st.subheader("📜 Generated Script")

        st.write(script)

        # =================================================
        # DISPLAY VIDEO
        # =================================================

        st.subheader("🎬 Generated Video")

        st.video(video_file)

        # =================================================
        # DOWNLOAD VIDEO
        # =================================================

        with open(video_file, "rb") as f:

            st.download_button(
                "⬇ Download Video",
                data=f,
                file_name="islamic_ai_video.mp4",
                mime="video/mp4"
            )

        # =================================================
        # DOWNLOAD SCRIPT
        # =================================================

        st.download_button(
            "⬇ Download Script",
            data=script,
            file_name="script.txt",
            mime="text/plain"
        )

    except Exception as e:

        st.error(f"Generation Failed: {e}")

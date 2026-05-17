import streamlit as st
from groq import Groq
from gtts import gTTS

from moviepy.editor import (
    VideoFileClip,
    AudioFileClip,
    ColorClip,
    CompositeVideoClip,
    ImageClip
)

from PIL import Image, ImageDraw, ImageFont
import numpy as np

import tempfile
import os
import textwrap

# ==========================================
# PAGE CONFIG
# ==========================================

st.set_page_config(
    page_title="Islamic Video Factory Ultimate",
    layout="wide"
)

# ==========================================
# CUSTOM CSS
# ==========================================

st.markdown("""
<style>
body {
    background-color: #021b12;
    color: white;
}

.stApp {
    background: linear-gradient(to bottom, #021b12, #041f18);
}

h1, h2, h3 {
    color: #00ff99;
}

.stButton>button {
    background-color: #00aa66;
    color: white;
    border-radius: 10px;
    font-weight: bold;
}

.stTextInput>div>div>input {
    background-color: #0b2b22;
    color: white;
}
</style>
""", unsafe_allow_html=True)

# ==========================================
# TITLE
# ==========================================

st.title("☪ Islamic Video Factory Ultimate")

st.write(
    "Generate cinematic Islamic AI videos with Groq + MoviePy"
)

# ==========================================
# API KEY
# ==========================================

try:
    GROQ_API_KEY = st.secrets["GROQ_API_KEY"]

    client = Groq(
        api_key=GROQ_API_KEY
    )

    st.success("✅ Groq API Connected")

except Exception as e:
    st.error(f"Groq API Error: {e}")
    st.stop()

# ==========================================
# SIDEBAR
# ==========================================

st.sidebar.title("Video Settings")

video_type = st.sidebar.selectbox(
    "Video Format",
    [
        "TikTok / Shorts",
        "YouTube"
    ]
)

video_length = st.sidebar.selectbox(
    "Video Length",
    [
        "30 Seconds",
        "1 Minute",
        "2 Minutes"
    ]
)

theme = st.sidebar.selectbox(
    "Theme",
    [
        "Motivational Reminder",
        "Historical Story",
        "Quranic Reflection",
        "Daily Duas"
    ]
)

topic = st.text_input(
    "Video Topic",
    "Motivation"
)

# ==========================================
# VIDEO SETTINGS
# ==========================================

duration_map = {
    "30 Seconds": 30,
    "1 Minute": 60,
    "2 Minutes": 120
}

target_duration = duration_map[video_length]

if video_type == "TikTok / Shorts":
    video_size = (720, 1280)
else:
    video_size = (1280, 720)

# ==========================================
# SCRIPT GENERATION
# ==========================================

def generate_script(topic, theme):

    system_prompt = f"""
You are an elite Islamic scholar and cinematic narrator.

Generate a powerful Islamic narration.

Rules:
- Never repeat wording
- Use Quranic wisdom
- Use emotional cinematic language
- Return narration only
- No numbering
- No stage directions
- No bullet points
"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "system",
                "content": system_prompt
            },
            {
                "role": "user",
                "content": f"""
Theme: {theme}

Topic: {topic}

Generate narration.
"""
            }
        ],
        temperature=1,
        max_tokens=1000
    )

    return response.choices[0].message.content

# ==========================================
# CREATE TEXT IMAGE
# ==========================================

def create_text_image(text, size):

    width, height = size

    img = Image.new(
        "RGBA",
        size,
        (0, 0, 0, 0)
    )

    draw = ImageDraw.Draw(img)

    try:
        font = ImageFont.truetype(
            "arial.ttf",
            45
        )
    except:
        font = ImageFont.load_default()

    wrapped = textwrap.fill(text, width=28)

    bbox = draw.multiline_textbbox(
        (0, 0),
        wrapped,
        font=font
    )

    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]

    x = (width - text_width) / 2
    y = height - 350

    draw.multiline_text(
        (x, y),
        wrapped,
        font=font,
        fill="white",
        align="center"
    )

    return np.array(img)

# ==========================================
# SAFE BACKGROUND LOADER
# ==========================================

def load_background(duration, size):

    try:

        if os.path.exists("background.mp4"):

            bg = VideoFileClip("background.mp4")

            bg = bg.resize(size)

            if bg.duration < duration:
                bg = bg.loop(duration=duration)

            bg = bg.subclip(0, duration)

            return bg

    except Exception as e:

        st.warning(
            f"Background video failed: {e}"
        )

    st.info("Using fallback cinematic background")

    return ColorClip(
        size=size,
        color=(5, 30, 20),
        duration=duration
    )

# ==========================================
# GENERATE VIDEO
# ==========================================

if st.button("Generate Cinematic Islamic Video"):

    with st.status(
        "Generating AI cinematic video...",
        expanded=True
    ) as status:

        try:

            st.write(
                "Step 1: Compiling narration via Groq..."
            )

            script = generate_script(
                topic,
                theme
            )

            st.subheader("Generated Script")
            st.write(script)

            st.write(
                "Step 2: Generating voice narration..."
            )

            tts = gTTS(script)

            temp_audio = tempfile.NamedTemporaryFile(
                delete=False,
                suffix=".mp3"
            )

            tts.save(temp_audio.name)

            audio = AudioFileClip(
                temp_audio.name
            )

            final_duration = audio.duration

            st.write(
                "Step 3: Processing cinematic visuals..."
            )

            background = load_background(
                final_duration,
                video_size
            )

            st.write(
                "Step 4: Rendering subtitles..."
            )

            text_img = create_text_image(
                topic,
                video_size
            )

            subtitle_clip = (
                ImageClip(text_img)
                .set_duration(final_duration)
            )

            final_video = CompositeVideoClip(
                [
                    background,
                    subtitle_clip
                ],
                size=video_size
            )

            final_video = final_video.set_audio(audio)

            st.write(
                "Step 5: Exporting MP4..."
            )

            output_path = os.path.join(
                tempfile.gettempdir(),
                "final_video.mp4"
            )

            final_video.write_videofile(
                output_path,
                fps=24,
                codec="libx264",
                audio_codec="aac",
                preset="ultrafast",
                threads=4,
                temp_audiofile="temp-audio.m4a",
                remove_temp=True
            )

            status.update(
                label="Video generation complete",
                state="complete"
            )

            st.success(
                "Video generated successfully"
            )

            # ==================================
            # SHOW VIDEO
            # ==================================

            st.subheader("Generated Video")

            video_file = open(
                output_path,
                "rb"
            )

            video_bytes = video_file.read()

            st.video(video_bytes)

            st.download_button(
                "Download Video",
                data=video_bytes,
                file_name="islamic_video.mp4",
                mime="video/mp4"
            )

            st.download_button(
                "Download Script",
                data=script,
                file_name="script.txt",
                mime="text/plain"
            )

        except Exception as e:

            st.error(
                f"Generation Failed: {e}"
            )

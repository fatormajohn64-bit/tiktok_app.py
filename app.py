# =========================================================
# ISLAMIC AI VIDEO FACTORY - PRO EDITION
# Streamlit + Gemini + MoviePy + Massive Memory
# =========================================================

import streamlit as st
import google.generativeai as genai
import os
import json
import time
import random
import hashlib
import tempfile
import numpy as np
import imageio_ffmpeg

from PIL import Image, ImageDraw, ImageFont

from moviepy.editor import (
    ColorClip,
    CompositeVideoClip,
    ImageClip,
    AudioFileClip
)

# =========================================================
# FFMPEG FIX
# =========================================================

os.environ["IMAGEIO_FFMPEG_EXE"] = imageio_ffmpeg.get_ffmpeg_exe()

# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="Islamic AI Video Factory",
    layout="wide"
)

# =========================================================
# CUSTOM CSS
# =========================================================

st.markdown("""
<style>

.stApp {
    background-color: #07120c;
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

</style>
""", unsafe_allow_html=True)

# =========================================================
# TITLE
# =========================================================

st.title("☪ Islamic AI Video Factory PRO")

st.write("Generate cinematic Islamic AI videos with Gemini.")

# =========================================================
# GEMINI API
# =========================================================

API_KEY = st.secrets["GEMINI_API_KEY"]

genai.configure(api_key=API_KEY)

# =========================================================
# SAFETY SETTINGS
# =========================================================

SAFETY_SETTINGS = [

    {
        "category": "HARM_CATEGORY_HARASSMENT",
        "threshold": "BLOCK_ONLY_HIGH"
    },

    {
        "category": "HARM_CATEGORY_HATE_SPEECH",
        "threshold": "BLOCK_ONLY_HIGH"
    },

    {
        "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
        "threshold": "BLOCK_ONLY_HIGH"
    },

    {
        "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
        "threshold": "BLOCK_ONLY_HIGH"
    }

]

# =========================================================
# MODEL DISCOVERY
# =========================================================

available_models = []

try:

    models = genai.list_models()

    for m in models:

        if "generateContent" in m.supported_generation_methods:

            available_models.append(m.name)

except Exception as e:

    st.error(f"Model Discovery Error: {e}")
    st.stop()

selected_model = None

priority = [
    "gemini-2.0-flash",
    "gemini-1.5-flash",
    "flash"
]

for p in priority:

    for m in available_models:

        if p.lower() in m.lower():

            selected_model = m
            break

    if selected_model:
        break

if not selected_model:

    st.error("No Gemini Flash model available.")
    st.write(available_models)
    st.stop()

# =========================================================
# INITIALIZE MODEL
# =========================================================

model = genai.GenerativeModel(
    selected_model,
    safety_settings=SAFETY_SETTINGS
)

st.success(f"Using Model: {selected_model}")

# =========================================================
# MEMORY SYSTEM
# =========================================================

MEMORY_FILE = "memory.json"

DEFAULT_MEMORY = {
    "used_hashes": [],
    "used_topics": [],
    "used_verses": []
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
# RETRY LOGIC
# =========================================================

def gemini_generate(prompt, retries=6):

    delay = 5

    for attempt in range(retries):

        try:

            response = model.generate_content(prompt)

            return response.text

        except Exception as e:

            if "429" in str(e):

                time.sleep(delay)

                delay *= 2

            else:

                raise e

    raise Exception("Gemini retry failed.")

# =========================================================
# ANTI REPEAT
# =========================================================

def already_used(text):

    text_hash = hashlib.md5(
        text.encode()
    ).hexdigest()

    return text_hash in memory["used_hashes"]

def save_hash(text):

    text_hash = hashlib.md5(
        text.encode()
    ).hexdigest()

    memory["used_hashes"].append(text_hash)

    save_memory(memory)

# =========================================================
# UI CONTROLS
# =========================================================

theme = st.selectbox(
    "Select Theme",
    [
        "Motivational",
        "Historical",
        "Educational",
        "Custom"
    ]
)

aspect_ratio = st.radio(
    "Aspect Ratio",
    [
        "9:16",
        "16:9"
    ]
)

topic = st.text_input(
    "Video Topic",
    placeholder="Example: Patience in Islam"
)

# =========================================================
# VIDEO DIMENSIONS
# =========================================================

if aspect_ratio == "9:16":

    VIDEO_WIDTH = 1080
    VIDEO_HEIGHT = 1920

else:

    VIDEO_WIDTH = 1920
    VIDEO_HEIGHT = 1080

# =========================================================
# GENERATE SCRIPT
# =========================================================

def generate_script():

    prompt = f"""
    Create a UNIQUE Islamic AI video.

    Theme:
    {theme}

    Topic:
    {topic}

    Requirements:
    - Emotional and cinematic
    - Include Quran verse
    - Include narration
    - Include Muslim character
    - Viral TikTok/YouTube style
    - 15-30 seconds
    - Never repeat content

    Avoid these used topics:
    {memory['used_topics'][-100:]}

    Avoid these used verses:
    {memory['used_verses'][-100:]}

    Output EXACTLY:

    TITLE:
    VERSE:
    NARRATION:
    """

    return gemini_generate(prompt)

# =========================================================
# PARSE SCRIPT
# =========================================================

def parse_script(text):

    data = {
        "TITLE": "",
        "VERSE": "",
        "NARRATION": ""
    }

    current = None

    for line in text.splitlines():

        line = line.strip()

        if line.startswith("TITLE:"):

            current = "TITLE"

            data[current] = line.replace(
                "TITLE:",
                ""
            ).strip()

        elif line.startswith("VERSE:"):

            current = "VERSE"

            data[current] = line.replace(
                "VERSE:",
                ""
            ).strip()

        elif line.startswith("NARRATION:"):

            current = "NARRATION"

            data[current] = line.replace(
                "NARRATION:",
                ""
            ).strip()

        elif current:

            data[current] += " " + line

    return data

# =========================================================
# CREATE VIDEO
# =========================================================

def create_video(title, verse, narration):

    duration = 20

    with tempfile.NamedTemporaryFile(
        suffix=".mp4",
        delete=False,
        dir="/tmp"
    ) as temp_video:

        output_path = temp_video.name

    # -----------------------------------------------------
    # BACKGROUND
    # -----------------------------------------------------

    background = ColorClip(
        size=(VIDEO_WIDTH, VIDEO_HEIGHT),
        color=(5, 5, 5),
        duration=duration
    )

    # -----------------------------------------------------
    # PIL IMAGE
    # -----------------------------------------------------

    img = Image.new(
        "RGBA",
        (VIDEO_WIDTH, VIDEO_HEIGHT),
        (0, 0, 0, 0)
    )

    draw = ImageDraw.Draw(img)

    # -----------------------------------------------------
    # FONTS
    # -----------------------------------------------------

    try:

        title_font = ImageFont.truetype(
            "DejaVuSans-Bold.ttf",
            70
        )

        verse_font = ImageFont.truetype(
            "DejaVuSans.ttf",
            50
        )

    except:

        title_font = ImageFont.load_default()
        verse_font = ImageFont.load_default()

    # -----------------------------------------------------
    # DRAW TEXT
    # -----------------------------------------------------

    draw.text(
        (80, 200),
        title,
        font=title_font,
        fill=(0, 208, 132, 255)
    )

    draw.text(
        (80, 600),
        verse,
        font=verse_font,
        fill=(255, 255, 255, 255)
    )

    draw.text(
        (80, 1000),
        narration,
        font=verse_font,
        fill=(220, 220, 220, 255)
    )

    # -----------------------------------------------------
    # PIL -> NUMPY
    # -----------------------------------------------------

    img_array = np.array(img)

    # -----------------------------------------------------
    # IMAGE CLIP
    # -----------------------------------------------------

    text_clip = (
        ImageClip(img_array)
        .set_duration(duration)
        .set_position(("center", "center"))
    )

    # -----------------------------------------------------
    # FINAL VIDEO
    # -----------------------------------------------------

    final_video = CompositeVideoClip([
        background,
        text_clip
    ])

    # -----------------------------------------------------
    # OPTIONAL AUDIO
    # -----------------------------------------------------

    if os.path.exists("nasheed.mp3"):

        audio = AudioFileClip(
            "nasheed.mp3"
        ).subclip(0, duration)

        final_video = final_video.set_audio(audio)

    # -----------------------------------------------------
    # EXPORT VIDEO
    # -----------------------------------------------------

    final_video.write_videofile(
        output_path,
        fps=30,
        codec="libx264",
        audio_codec="aac",
        bitrate="8000k"
    )

    return output_path

# =========================================================
# GENERATE BUTTON
# =========================================================

if st.button("Generate Islamic Video"):

    try:

        with st.status(
            "Generating Islamic AI Video...",
            expanded=True
        ) as status:

            # -------------------------------------------------
            # STEP 1
            # -------------------------------------------------

            st.write("Generating script...")

            raw_script = generate_script()

            parsed = parse_script(raw_script)

            title = parsed["TITLE"]
            verse = parsed["VERSE"]
            narration = parsed["NARRATION"]

            save_hash(raw_script)

            memory["used_topics"].append(title)
            memory["used_verses"].append(verse)

            save_memory(memory)

            # -------------------------------------------------
            # STEP 2
            # -------------------------------------------------

            st.write("Creating cinematic video...")

            video_path = create_video(
                title,
                verse,
                narration
            )

            # -------------------------------------------------
            # COMPLETE
            # -------------------------------------------------

            status.update(
                label="Video Generated Successfully",
                state="complete"
            )

        # -----------------------------------------------------
        # DISPLAY RESULTS
        # -----------------------------------------------------

        st.subheader("Generated Script")

        st.write(parsed)

        st.video(video_path)

        with open(video_path, "rb") as f:

            st.download_button(
                label="Download HD Video",
                data=f,
                file_name="islamic_ai_video.mp4",
                mime="video/mp4"
            )

    except Exception as e:

        st.error("Generation Failed")

        st.code(str(e))

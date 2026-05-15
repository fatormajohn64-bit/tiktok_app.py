# =========================================================
# ISLAMIC AI VIDEO FACTORY - MASTER VERSION
# Streamlit + Gemini + Anti-Repeat + HD Export
# =========================================================

import streamlit as st
import google.generativeai as genai
import os
import json
import random
import time
import hashlib
import requests
import imageio_ffmpeg
from datetime import datetime
from moviepy.editor import *
from PIL import Image, ImageDraw, ImageFont

# =========================================================
# FFMPEG FIX
# =========================================================

os.environ["IMAGEIO_FFMPEG_EXE"] = imageio_ffmpeg.get_ffmpeg_exe()

# =========================================================
# STREAMLIT CONFIG
# =========================================================

st.set_page_config(
    page_title="Islamic AI Video Factory",
    layout="wide"
)

# =========================================================
# SECRETS
# =========================================================

GENAI_API_KEY = "your_actual_api_key_here"


# =========================================================
# GEMINI CONFIG
# =========================================================

genai.configure(api_key=API_KEY)


# =========================================================
# AUTO MODEL DETECTION
# =========================================================

available_models = []

try:
    models = genai.list_models()

    for m in models:
        if "generateContent" in m.supported_generation_methods:
            available_models.append(m.name)

except Exception as e:
    st.error(e)
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
    st.error("No Gemini Flash model found.")
    st.write(available_models)
    st.stop()

model = genai.GenerativeModel(selected_model)

# =========================================================
# MASSIVE MEMORY SYSTEM
# =========================================================

MEMORY_FILE = "islamic_memory.json"

DEFAULT_MEMORY = {
    "used_topics": [],
    "used_verses": [],
    "used_visuals": [],
    "used_hashes": [],
    "generated_videos": []
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
# QURAN KNOWLEDGE
# =========================================================

QURAN_TOPICS = [
    "Mercy of Allah",
    "Prayer",
    "Patience",
    "Jannah",
    "Repentance",
    "Forgiveness",
    "Death",
    "Guidance",
    "Faith",
    "Trust in Allah",
    "Charity",
    "Hope",
    "Fear of Allah",
    "Day of Judgment",
    "Islamic Brotherhood",
    "Tahajjud",
    "Quran Healing",
    "Power of Dua",
    "Parents in Islam",
    "Marriage in Islam"
]

VISUAL_STYLES = [
    "cinematic desert",
    "Islamic mosque night scene",
    "Muslim man talking emotionally",
    "Muslim woman making dua",
    "beautiful Quran closeup",
    "golden Islamic calligraphy",
    "sunrise prayer scene",
    "rainy emotional cinematic scene",
    "Arabic city cinematic",
    "dark emotional spiritual scene"
]

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
# ANTI-REPEAT ENGINE
# =========================================================

def content_exists(text):

    content_hash = hashlib.md5(
        text.encode()
    ).hexdigest()

    return content_hash in memory["used_hashes"]

def save_hash(text):

    content_hash = hashlib.md5(
        text.encode()
    ).hexdigest()

    memory["used_hashes"].append(content_hash)

    save_memory(memory)

# =========================================================
# GENERATE UNIQUE ISLAMIC CONTENT
# =========================================================

def generate_unique_video():

    attempts = 0

    while attempts < 10:

        topic = random.choice(QURAN_TOPICS)
        style = random.choice(VISUAL_STYLES)

        prompt = f"""
        Create a completely UNIQUE Islamic TikTok video.

        Rules:
        - Never repeat previous ideas
        - Emotional and cinematic
        - 15-30 seconds
        - Add Quran verse
        - Add narration
        - Add scene descriptions
        - Main character should be Muslim
        - Add cinematic emotions
        - High engagement TikTok style

        Previously used topics:
        {memory['used_topics'][-100:]}

        Previously used verses:
        {memory['used_verses'][-100:]}

        Topic:
        {topic}

        Visual style:
        {style}

        Output format:

        TITLE:
        VERSE:
        NARRATION:
        SCENES:
        """

        result = gemini_generate(prompt)

        if not content_exists(result):

            save_hash(result)

            return result

        attempts += 1

    raise Exception("Could not generate unique content.")

# =========================================================
# PARSE AI OUTPUT
# =========================================================

def parse_content(text):

    sections = {
        "TITLE": "",
        "VERSE": "",
        "NARRATION": "",
        "SCENES": ""
    }

    current = None

    for line in text.splitlines():

        line = line.strip()

        if line.startswith("TITLE:"):
            current = "TITLE"
            sections[current] = line.replace("TITLE:", "").strip()

        elif line.startswith("VERSE:"):
            current = "VERSE"
            sections[current] = line.replace("VERSE:", "").strip()

        elif line.startswith("NARRATION:"):
            current = "NARRATION"
            sections[current] = line.replace("NARRATION:", "").strip()

        elif line.startswith("SCENES:"):
            current = "SCENES"
            sections[current] = line.replace("SCENES:", "").strip()

        elif current:
            sections[current] += " " + line

    return sections

# =========================================================
# CREATE HD VIDEO
# =========================================================

def create_video(data):

    title = data["TITLE"]
    verse = data["VERSE"]
    narration = data["NARRATION"]

    width = 1080
    height = 1920
    duration = 20

    background = ColorClip(
        size=(width, height),
        color=(0, 0, 0),
        duration=duration
    )

    title_clip = TextClip(
        title,
        fontsize=80,
        color="gold",
        method="caption",
        size=(900, None)
    ).set_position(("center", 250)).set_duration(duration)

    verse_clip = TextClip(
        verse,
        fontsize=55,
        color="white",
        method="caption",
        size=(900, None)
    ).set_position(("center", 700)).set_duration(duration)

    narration_clip = TextClip(
        narration,
        fontsize=50,
        color="white",
        method="caption",
        size=(950, None)
    ).set_position(("center", 1200)).set_duration(duration)

    final = CompositeVideoClip([
        background,
        title_clip.fadein(1),
        verse_clip.fadein(2),
        narration_clip.fadein(3)
    ])

    # OPTIONAL NASHEED
    if os.path.exists("nasheed.mp3"):

        audio = AudioFileClip("nasheed.mp3")

        final = final.set_audio(
            audio.subclip(0, duration)
        )

    filename = f"video_{int(time.time())}.mp4"

    final.write_videofile(
        filename,
        fps=30,
        codec="libx264",
        audio_codec="aac",
        bitrate="8000k"
    )

    return filename

# =========================================================
# STREAMLIT UI
# =========================================================

st.title("☪ Islamic AI Video Factory")

st.write("Generate Unlimited Unique Islamic TikTok Videos")

st.success(f"Using Model: {selected_model}")

# =========================================================
# GENERATE BUTTON
# =========================================================

if st.button("Generate New Islamic Video"):

    with st.spinner("Generating unique Islamic AI video..."):

        try:

            raw = generate_unique_video()

            data = parse_content(raw)

            st.subheader("Generated Script")

            st.write(data)

            video_path = create_video(data)

            # SAVE MEMORY
            memory["used_topics"].append(data["TITLE"])
            memory["used_verses"].append(data["VERSE"])
            memory["generated_videos"].append(video_path)

            save_memory(memory)

            st.success("Video Created Successfully")

            st.video(video_path)

            with open(video_path, "rb") as f:

                st.download_button(
                    label="Download HD Video",
                    data=f,
                    file_name=video_path,
                    mime="video/mp4"
                )

        except Exception as e:

            st.error(str(e))

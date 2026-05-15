# =========================================================
# ISLAMIC AI VIDEO FACTORY - FINAL MASTER VERSION
# Streamlit + Gemini + Massive Memory + No ImageMagick
# =========================================================

import streamlit as st
import google.generativeai as genai
import os
import json
import random
import time
import hashlib
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
# STREAMLIT CONFIG
# =========================================================

st.set_page_config(
    page_title="Islamic AI Video Factory",
    layout="wide"
)

st.title("☪ Islamic AI Video Factory")

# =========================================================
# GEMINI API KEY
# =========================================================

API_KEY = st.secrets["GEMINI_API_KEY"]

# =========================================================
# GEMINI CONFIG
# =========================================================

genai.configure(api_key=API_KEY)

# =========================================================
# AUTO FIND WORKING MODEL
# =========================================================

available_models = []

try:

    models = genai.list_models()

    for m in models:

        if "generateContent" in m.supported_generation_methods:

            available_models.append(m.name)

except Exception as e:

    st.error(f"Gemini Model Error: {e}")
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

    st.error("No compatible Gemini model found.")
    st.write(available_models)
    st.stop()

# =========================================================
# INITIALIZE MODEL
# =========================================================

try:

    model = genai.GenerativeModel(selected_model)

except Exception as e:

    st.error(e)
    st.write(available_models)
    st.stop()

st.success(f"Using Model: {selected_model}")

# =========================================================
# MASSIVE MEMORY SYSTEM
# =========================================================

MEMORY_FILE = "memory.json"

DEFAULT_MEMORY = {
    "used_hashes": [],
    "used_titles": [],
    "used_verses": [],
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
# RETRY LOGIC FOR 429 ERRORS
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
# QURAN TOPICS
# =========================================================

TOPICS = [

    "Mercy of Allah",
    "Forgiveness",
    "Prayer",
    "Trust in Allah",
    "Death",
    "Repentance",
    "Patience",
    "Tahajjud",
    "Jannah",
    "Islamic Motivation",
    "Power of Dua",
    "Islamic Brotherhood",
    "Quran Healing",
    "Day of Judgment",
    "Fear of Allah",
    "Charity",
    "Hope in Allah",
    "Islamic Love",
    "Parents in Islam",
    "Marriage in Islam"

]

VISUALS = [

    "Muslim man speaking emotionally",
    "Islamic cinematic desert",
    "Muslim praying at sunrise",
    "Beautiful Quran closeup",
    "Rainy emotional Islamic scene",
    "Mosque cinematic night scene",
    "Arabic city cinematic shot",
    "Muslim making dua crying",
    "Golden Islamic calligraphy",
    "Powerful Islamic speech scene"

]

# =========================================================
# GENERATE UNIQUE ISLAMIC CONTENT
# =========================================================

def generate_content():

    attempts = 0

    while attempts < 10:

        topic = random.choice(TOPICS)

        visual = random.choice(VISUALS)

        prompt = f"""
        Create a UNIQUE Islamic TikTok video script.

        Rules:
        - Never repeat ideas
        - Emotional and cinematic
        - 15-30 seconds
        - Include Quran verse
        - Include narration
        - Include cinematic visuals
        - Include Muslim character
        - TikTok viral style

        Avoid these used titles:
        {memory['used_titles'][-100:]}

        Avoid these used verses:
        {memory['used_verses'][-100:]}

        Topic:
        {topic}

        Visual Style:
        {visual}

        Output EXACTLY like this:

        TITLE:
        VERSE:
        NARRATION:
        """

        result = gemini_generate(prompt)

        if not already_used(result):

            save_hash(result)

            return result

        attempts += 1

    raise Exception("Failed to create unique content.")

# =========================================================
# PARSE AI RESPONSE
# =========================================================

def parse_content(text):

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
# VIDEO CREATOR
# NO TEXTCLIP / NO IMAGEMAGICK
# =========================================================

def create_video(caption_text, verse_text, output_filename):

    VIDEO_WIDTH = 1080
    VIDEO_HEIGHT = 1920
    DURATION = 20

    # -----------------------------------------------------
    # BACKGROUND
    # -----------------------------------------------------

    background = ColorClip(
        size=(VIDEO_WIDTH, VIDEO_HEIGHT),
        color=(10, 10, 10),
        duration=DURATION
    )

    # -----------------------------------------------------
    # CREATE PIL IMAGE
    # -----------------------------------------------------

    img_width = 1000
    img_height = 1400

    pil_img = Image.new(
        "RGBA",
        (img_width, img_height),
        (0, 0, 0, 0)
    )

    draw = ImageDraw.Draw(pil_img)

    # -----------------------------------------------------
    # FONT
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
    # DRAW TITLE
    # -----------------------------------------------------

    draw.text(
        (60, 250),
        caption_text,
        font=title_font,
        fill=(255, 215, 0, 255)
    )

    # -----------------------------------------------------
    # DRAW VERSE
    # -----------------------------------------------------

    draw.text(
        (60, 700),
        verse_text,
        font=verse_font,
        fill=(255, 255, 255, 255)
    )

    # -----------------------------------------------------
    # PIL -> NUMPY
    # -----------------------------------------------------

    img_array = np.array(pil_img)

    # -----------------------------------------------------
    # IMAGE CLIP
    # -----------------------------------------------------

    text_clip = (
        ImageClip(img_array)
        .set_duration(DURATION)
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
        ).subclip(0, DURATION)

        final_video = final_video.set_audio(audio)

    # -----------------------------------------------------
    # EXPORT HD VIDEO
    # -----------------------------------------------------

    final_video.write_videofile(
        output_filename,
        fps=30,
        codec="libx264",
        audio_codec="aac",
        bitrate="8000k"
    )

    return output_filename

# =========================================================
# STREAMLIT BUTTON
# =========================================================

if st.button("Generate Islamic Video"):

    with st.spinner("Generating Islamic AI Video..."):

        try:

            raw = generate_content()

            data = parse_content(raw)

            title = data["TITLE"]
            verse = data["VERSE"]
            narration = data["NARRATION"]

            st.subheader("Generated Script")

            st.write(data)

            filename = f"video_{int(time.time())}.mp4"

            create_video(
                narration,
                verse,
                filename
            )

            # SAVE MEMORY
            memory["used_titles"].append(title)
            memory["used_verses"].append(verse)
            memory["generated_videos"].append(filename)

            save_memory(memory)

            st.success("Video Generated Successfully")

            st.video(filename)

            with open(filename, "rb") as f:

                st.download_button(
                    label="Download HD Video",
                    data=f,
                    file_name=filename,
                    mime="video/mp4"
                )

        except Exception as e:

            st.error(str(e))

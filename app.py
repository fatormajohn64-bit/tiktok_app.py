import streamlit as st
import os
import json
import random
from datetime import datetime
from groq import Groq
from moviepy.editor import (
    VideoFileClip,
    AudioFileClip,
    CompositeVideoClip,
    TextClip,
    CompositeAudioClip,
)
from gtts import gTTS

# =========================
# PAGE CONFIG
# =========================
st.set_page_config(
    page_title="Islamic Video Factory Ultimate",
    page_icon="☪️",
    layout="centered"
)

# =========================
# CUSTOM STYLE
# =========================
st.markdown(
    """
    <style>
    .stApp {
        background: linear-gradient(to bottom, #031b12, #072f1f);
        color: white;
    }
    h1,h2,h3 {
        color: #00ff99;
    }
    .stButton>button {
        background-color: #00aa66;
        color: white;
        border-radius: 12px;
        border: none;
        padding: 10px 20px;
        font-size: 18px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# =========================
# MEMORY SYSTEM
# =========================
MEMORY_FILE = "memory.json"

if not os.path.exists(MEMORY_FILE):
    with open(MEMORY_FILE, "w") as f:
        json.dump([], f)


def save_memory(topic, script_text):
    with open(MEMORY_FILE, "r") as f:
        data = json.load(f)

    data.append({
        "topic": topic,
        "script": script_text,
        "time": str(datetime.now())
    })

    with open(MEMORY_FILE, "w") as f:
        json.dump(data, f, indent=4)


def load_memory():
    with open(MEMORY_FILE, "r") as f:
        return json.load(f)

# =========================
# API KEY
# =========================
try:
    GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
    client = Groq(api_key=GROQ_API_KEY)
    st.success("✅ Groq API Connected")
except Exception as e:
    st.error("❌ Groq API Key Missing")
    st.stop()

# =========================
# TITLE
# =========================
st.title("☪️ Islamic Video Factory Ultimate")
st.write("Generate cinematic Islamic AI videos with Groq + MoviePy")

# =========================
# INPUT
# =========================
topic = st.text_input(
    "Video Topic",
    placeholder="Motivation, Tawakkul, Patience, Prayer..."
)

# =========================
# VIDEO GENERATION
# =========================
if st.button("Generate Cinematic Islamic Video"):

    if topic.strip() == "":
        st.warning("Please enter a topic")
        st.stop()

    try:
        with st.status("🎬 Generating AI cinematic video...", expanded=True) as status:

            # =========================
            # STEP 1 — SCRIPT
            # =========================
            st.write("Step 1: Compiling narration via Groq...")

            prompt = f"""
            Create a powerful cinematic Islamic motivational narration about:
            {topic}

            Rules:
            - emotional
            - deep
            - inspiring
            - short TikTok style
            - around 120 words
            - cinematic narration style
            - no markdown
            """

            response = client.chat.completions.create(
                model="llama3-70b-8192",
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )

            script = response.choices[0].message.content

            st.subheader("📜 Generated Script")
            st.write(script)

            # SAVE MEMORY
            save_memory(topic, script)

            # =========================
            # STEP 2 — VOICE
            # =========================
            st.write("Step 2: Generating voice narration...")

            tts = gTTS(script)
            tts.save("voice.mp3")

            audio = AudioFileClip("voice.mp3")
            duration = audio.duration

            # =========================
            # STEP 3 — VIDEO
            # =========================
            st.write("Step 3: Processing cinematic visuals...")

            background_path = "background.mp4"

            if not os.path.exists(background_path):
                st.error("background.mp4 not found")
                st.stop()

            background = VideoFileClip(background_path)

            # Resize vertical TikTok
            background = background.resize((720, 1280))

            # Match audio duration
            if background.duration < duration:
                loops = int(duration / background.duration) + 1
                clips = [background] * loops
                from moviepy.editor import concatenate_videoclips
                background = concatenate_videoclips(clips)

            background = background.subclip(0, duration)

            # =========================
            # TEXT OVERLAY
            # =========================
            split_script = script[:180]

            txt = TextClip(
                split_script,
                fontsize=50,
                color='white',
                method='caption',
                size=(650, None),
                align='center'
            ).set_position(('center', 'bottom')).set_duration(duration)

            # =========================
            # FINAL VIDEO
            # =========================
            final = CompositeVideoClip([
                background,
                txt
            ])

            final = final.set_audio(audio)

            output_file = f"video_{random.randint(1000,9999)}.mp4"

            final.write_videofile(
                output_file,
                fps=30,
                codec="libx264",
                audio_codec="aac"
            )

            status.update(label="✅ Video generation completed", state="complete")

            # =========================
            # SHOW VIDEO
            # =========================
            st.subheader("🎥 Generated Video")

            video_file = open(output_file, 'rb')
            st.video(video_file.read())

            with open(output_file, "rb") as file:
                st.download_button(
                    label="⬇ Download Video",
                    data=file,
                    file_name=output_file,
                    mime="video/mp4"
                )

    except Exception as e:
        st.error(f"Generation Failed: {e}")

# =========================
# MEMORY VIEWER
# =========================
st.divider()

st.subheader("🧠 AI Memory")

memories = load_memory()

if len(memories) > 0:
    for item in reversed(memories[-5:]):
        with st.expander(item["topic"]):
            st.write(item["script"])
            st.caption(item["time"])
else:
    st.info("No memory yet")

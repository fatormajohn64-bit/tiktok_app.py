import streamlit as st
import os
import json
from datetime import datetime
from groq import Groq
from gtts import gTTS
from moviepy.editor import VideoFileClip, AudioFileClip

# =========================
# PAGE CONFIG
# =========================

st.set_page_config(
    page_title="Islamic Video Factory Ultimate",
    layout="wide"
)

# =========================
# CUSTOM STYLE
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
# API SETUP
# =========================

try:
    GROQ_API_KEY = st.secrets["GROQ_API_KEY"]

    client = Groq(
        api_key=GROQ_API_KEY
    )

    st.success("✅ Groq API Connected")

except Exception as e:
    st.error(f"Groq API Error: {e}")
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
# INPUT
# =========================

topic = st.text_input(
    "Video Topic",
    "Motivation"
)

# =========================
# GENERATE VIDEO
# =========================

if st.button("Generate Cinematic Islamic Video"):

    try:

        st.info("🎬 Generating AI cinematic video...")

        # =========================
        # STEP 1 — GENERATE SCRIPT
        # =========================

        st.write("Step 1: Compiling narration via Groq...")

        prompt = f"""
        Create a powerful cinematic Islamic motivational narration about:
        {topic}

        Make it emotional, spiritual, inspirational,
        deep, and suitable for TikTok cinematic narration.
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
            max_tokens=500
        )

        script = response.choices[0].message.content

        st.success("✅ Narration Generated")
        st.write(script)

        # =========================
        # SAVE MEMORY
        # =========================

        save_memory(topic, script)

        # =========================
        # STEP 2 — TEXT TO SPEECH
        # =========================

        st.write("Step 2: Generating voice narration...")

        tts = gTTS(text=script, lang="en")

        audio_path = "voice.mp3"

        tts.save(audio_path)

        # =========================
        # STEP 3 — LOAD VIDEO
        # =========================

        st.write("Step 3: Processing cinematic visuals...")

        background_video = "background.mp4"

        if not os.path.exists(background_video):
            st.error("❌ background.mp4 not found")
            st.stop()

        video = VideoFileClip(background_video)

        audio = AudioFileClip(audio_path)

        final_video = video.set_audio(audio)

        output_path = "final_video.mp4"

        final_video.write_videofile(
            output_path,
            codec="libx264",
            audio_codec="aac"
        )

        # =========================
        # SUCCESS
        # =========================

        st.success("✅ Video Generated Successfully")

        st.video(output_path)

        with open(output_path, "rb") as file:
            st.download_button(
                "⬇ Download Video",
                file,
                file_name="islamic_ai_video.mp4"
            )

    except Exception as e:
        st.error(f"Generation Failed: {e}")

# =========================
# MEMORY DISPLAY
# =========================

st.markdown("---")
st.header("🧠 AI Memory")

memory = load_memory()

if len(memory) == 0:
    st.info("No memory yet")

else:

    for item in reversed(memory[-10:]):

        with st.expander(item["topic"]):

            st.markdown(f"""
            <div class="memory-box">
            {item["script"]}
            <br><br>
            <b>Time:</b> {item["time"]}
            </div>
            """, unsafe_allow_html=True)

# =========================================================
# ISLAMIC VIDEO CONTENT FACTORY ULTIMATE
# STREAMLIT + GROQ + MOVIEPY + GTTS
# =========================================================

import os
import json
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
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="Islamic Video Factory Ultimate",
    layout="wide"
)

# =========================================================
# DARK ISLAMIC UI
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
    padding: 0.7rem 1rem;
}

section[data-testid="stSidebar"] {
    background-color: #08140d;
}

</style>
""", unsafe_allow_html=True)

# =========================================================
# TITLE
# =========================================================

st.title("☪ Islamic Video Factory Ultimate")

st.write(
    "Generate unlimited cinematic Islamic AI videos with Groq + Llama 3.3 70B."
)

# =========================================================
# API SETUP
# =========================================================

try:

    GROQ_API_KEY = st.secrets["GROQ_API_KEY"]

    client = Groq(
        api_key=GROQ_API_KEY
    )

    st.success("Groq Connected Successfully")

except Exception as e:

    st.error(f"Groq API Error: {e}")
    st.stop()

# =========================================================
# MEMORY SYSTEM
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

st.sidebar.title("Video Controls")

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
# DURATION MAP
# =========================================================

duration_map = {

    "30 Seconds": 30,
    "1 Minute": 60,
    "2 Minutes": 120,
    "5 Minutes": 300,
    "10 Minutes": 600

}

TARGET_DURATION = duration_map[video_length]

# =========================================================
# MASSIVE SYSTEM PROMPT
# =========================================================

SYSTEM_PROMPT = """

You are an elite Islamic scholar,
cinematic storyteller,
historian,
Quran expert,
and emotional motivational speaker.

You possess deep knowledge of:

- Quran Tafsir
- Authentic Hadith
- Sahih Bukhari
- Sahih Muslim
- Islamic History
- Seerah of Prophet Muhammad ﷺ
- The Companions
- Spiritual purification
- Islamic reflections
- Emotional reminders
- Islamic Golden Age

CRITICAL RULES:

- NEVER repeat scripts
- NEVER reuse hooks
- NEVER duplicate paragraph structures
- Use diverse storytelling styles
- Use emotional cinematic pacing
- Generate highly unique scripts every time
- Create viral social media style narration
- Use deep emotional hooks
- Use strong endings

STRICT OUTPUT RULE:

Return ONLY spoken narration text.

DO NOT include:
- Bullet points
- Labels
- Director notes
- Scene numbers
- Brackets
- Titles

The narration must sound natural for text-to-speech.

"""

# =========================================================
# SCRIPT GENERATION
# =========================================================

@st.cache_data(show_spinner=False)
def generate_script(topic, theme, video_length):

    user_prompt = f"""

    Topic:
    {topic}

    Theme:
    {theme}

    Length:
    {video_length}

    Requirements:

    - Emotional narration
    - Cinematic pacing
    - Deep Islamic reflections
    - Viral social media hooks
    - Realistic storytelling
    - Powerful emotional ending

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

        temperature=1.2,
        max_tokens=4000

    )

    return response.choices[0].message.content

# =========================================================
# SAVE HASH
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

    # =====================================================
    # TRY BACKGROUND VIDEO
    # =====================================================

    background = None

    if os.path.exists("background.mp4"):

        try:

            background = VideoFileClip(
                "background.mp4"
            ).subclip(0, TARGET_DURATION)

        except Exception:

            background = None

    # =====================================================
    # FALLBACK COLOR BACKGROUND
    # =====================================================

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

    # =====================================================
    # COMBINE AUDIO + VIDEO
    # =====================================================

    final_video = CompositeVideoClip([
        background
    ])

    final_video = final_video.set_audio(audio_clip)

    # =====================================================
    # EXPORT VIDEO
    # =====================================================

    final_video.write_videofile(

        output_path,

        fps=24,

        codec="libx264",

        audio_codec="aac",

        bitrate="5000k"

    )

    return output_path

# =========================================================
# SCRIPT DOWNLOAD
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

            # =================================================
            # STEP 1 - GENERATE SCRIPT
            # =================================================

            st.write("Generating cinematic narration...")

            script = generate_script(
                topic,
                theme,
                video_length
            )

            save_hash(script)

            memory["used_topics"].append(topic)

            save_memory(memory)

            # =================================================
            # STEP 2 - CREATE VOICE
            # =================================================

            st.write("Generating voiceover...")

            audio_path = create_voiceover(script)

            # =================================================
            # STEP 3 - CREATE VIDEO
            # =================================================

            st.write("Rendering cinematic video...")

            video_path = create_video(audio_path)

            # =================================================
            # COMPLETE
            # =================================================

            status.update(
                label="Video Generation Complete",
                state="complete"
            )

        # =====================================================
        # DISPLAY SCRIPT
        # =====================================================

        st.subheader("Generated Narration")

        st.text_area(
            "Narration Script",
            script,
            height=350
        )

        # =====================================================
        # DISPLAY VIDEO
        # =====================================================

        st.subheader("Generated Video")

        st.video(video_path)

        # =====================================================
        # DOWNLOAD VIDEO
        # =====================================================

        with open(video_path, "rb") as f:

            st.download_button(

                label="Download Video",

                data=f,

                file_name="islamic_video.mp4",

                mime="video/mp4"

            )

        # =====================================================
        # DOWNLOAD SCRIPT
        # =====================================================

        st.download_button(

            label="Download Script",

            data=script_download(script),

            file_name="islamic_script.txt",

            mime="text/plain"

        )

    except Exception as e:

        st.error("Generation Failed")

        st.code(str(e))

# =========================================================
# ISLAMIC VIDEO CONTENT FACTORY PRO
# Gemini 2.0 Flash + Streamlit + Massive Memory
# =========================================================

import os
import json
import time
import hashlib
import tempfile
import streamlit as st
import google.generativeai as genai
import imageio_ffmpeg

from moviepy.editor import (
    VideoFileClip,
    CompositeVideoClip
)

# =========================================================
# FFMPEG FIX
# =========================================================

os.environ["IMAGEIO_FFMPEG_EXE"] = imageio_ffmpeg.get_ffmpeg_exe()

# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="Islamic Video Content Factory",
    layout="wide"
)

# =========================================================
# DARK UI
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
    "Generate unlimited cinematic Islamic videos using Gemini 2.0 Flash."
)

# =========================================================
# GEMINI CONFIG
# =========================================================

API_KEY = st.secrets["GEMINI_API_KEY"]

genai.configure(api_key=API_KEY)

# =========================================================
# SAFETY SETTINGS
# =========================================================

SAFETY_SETTINGS = [

    {
        "category": "HARM_CATEGORY_HARASSMENT",
        "threshold": "BLOCK_NONE"
    },

    {
        "category": "HARM_CATEGORY_HATE_SPEECH",
        "threshold": "BLOCK_NONE"
    },

    {
        "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
        "threshold": "BLOCK_NONE"
    },

    {
        "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
        "threshold": "BLOCK_NONE"
    }

]

# =========================================================
# SMART MODEL SELECTION
# =========================================================

available_models = []

try:

    models = genai.list_models()

    for m in models:

        if "generateContent" in m.supported_generation_methods:

            available_models.append(m.name)

except Exception as e:

    st.error(f"Model Error: {e}")
    st.stop()

selected_model = None

priority = [
    "gemini-2.0-flash",
    "gemini-1.5-flash",
    "flash"
]

for p in priority:

    for model_name in available_models:

        if p.lower() in model_name.lower():

            selected_model = model_name
            break

    if selected_model:
        break

if not selected_model:

    st.error("No Gemini Flash model found.")
    st.write(available_models)
    st.stop()

# =========================================================
# SYSTEM INSTRUCTION
# =========================================================

SYSTEM_INSTRUCTION = """

You are the world's greatest Islamic cinematic scriptwriter.

Your job is to create:

- Emotional Islamic stories
- Quranic reminders
- Historical Islamic lessons
- Motivational Islamic speeches
- Deep reflections about Allah
- Realistic cinematic scene directions

RULES:

- NEVER repeat stories
- NEVER repeat verses frequently
- Use deep Islamic knowledge
- Use emotional hooks
- Use cinematic realism
- Use viral storytelling
- Every scene must include:
    - Narration
    - Director notes
    - Camera angle
    - Lighting
    - Visual realism
    - AI image prompt

STYLE:

- Cinematic
- Emotional
- Hollywood realism
- 4K visual language
- Epic atmosphere
- Viral TikTok pacing

"""

# =========================================================
# MODEL INIT
# =========================================================

model = genai.GenerativeModel(
    model_name=selected_model,
    system_instruction=SYSTEM_INSTRUCTION,
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
# SIDEBAR
# =========================================================

st.sidebar.title("Video Controls")

video_type = st.sidebar.selectbox(
    "Video Format",
    [
        "TikTok / Shorts",
        "YouTube Long-form"
    ]
)

if video_type == "TikTok / Shorts":

    duration = st.sidebar.selectbox(
        "Length",
        [
            "1 Minute",
            "2 Minutes",
            "5 Minutes"
        ]
    )

else:

    duration = st.sidebar.selectbox(
        "Length",
        [
            "10 Minutes",
            "15 Minutes",
            "20 Minutes"
        ]
    )

topic = st.sidebar.text_input(
    "Video Topic",
    placeholder="Example: Tawakkul in Islam"
)

# =========================================================
# FLASH OPTIMIZED PROMPT
# =========================================================

PROMPT_TEMPLATE = """

Topic:
{topic}

Video Type:
{video_type}

Length:
{duration}

Requirements:

- Create highly emotional Islamic content
- Include Quranic wisdom
- Include cinematic narration
- Include cinematic director notes
- Include realistic AI image prompts
- Include viral hooks
- Include emotional storytelling
- Include transitions
- Include scene numbers
- Include realism instructions

Avoid these topics:
{used_topics}

Avoid these verses:
{used_verses}

FORMAT:

TITLE:

HOOK:

SCENE 1:
Narration:
Director Notes:
Image Prompt:

SCENE 2:
Narration:
Director Notes:
Image Prompt:

Continue until complete.

ENDING:
Call to Action:

"""

# =========================================================
# CACHE SCRIPT
# =========================================================

@st.cache_data(show_spinner=False)
def generate_script_cached(prompt):

    response = model.generate_content(prompt)

    return response.text

# =========================================================
# GENERATE SCRIPT
# =========================================================

def generate_script():

    prompt = PROMPT_TEMPLATE.format(
        topic=topic,
        video_type=video_type,
        duration=duration,
        used_topics=memory["used_topics"][-100:],
        used_verses=memory["used_verses"][-100:]
    )

    response = generate_script_cached(prompt)

    return response

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
# VIDEO PREVIEW
# =========================================================

def create_preview():

    if not os.path.exists("background.mp4"):

        return None

    with tempfile.NamedTemporaryFile(
        suffix=".mp4",
        delete=False,
        dir="/tmp"
    ) as temp_video:

        output_path = temp_video.name

    background = VideoFileClip(
        "background.mp4"
    ).subclip(0, 15)

    final = CompositeVideoClip([
        background
    ])

    final.write_videofile(
        output_path,
        codec="libx264",
        audio_codec="aac"
    )

    return output_path

# =========================================================
# PDF DOWNLOAD
# =========================================================

def build_text_download(script):

    return script.encode("utf-8")

# =========================================================
# GENERATE BUTTON
# =========================================================

if st.button("Generate Cinematic Islamic Video"):

    try:

        with st.status(
            "Generating cinematic Islamic content...",
            expanded=True
        ) as status:

            # -------------------------------------------------
            # STEP 1
            # -------------------------------------------------

            st.write("Generating cinematic script...")

            script = generate_script()

            save_hash(script)

            memory["used_topics"].append(topic)

            save_memory(memory)

            # -------------------------------------------------
            # STEP 2
            # -------------------------------------------------

            st.write("Creating video preview...")

            preview_path = create_preview()

            # -------------------------------------------------
            # COMPLETE
            # -------------------------------------------------

            status.update(
                label="Generation Complete",
                state="complete"
            )

        # -----------------------------------------------------
        # DISPLAY SCRIPT
        # -----------------------------------------------------

        st.subheader("Generated Cinematic Script")

        st.text_area(
            "Script Output",
            script,
            height=600
        )

        # -----------------------------------------------------
        # VIDEO PREVIEW
        # -----------------------------------------------------

        if preview_path:

            st.subheader("Video Preview")

            st.video(preview_path)

        # -----------------------------------------------------
        # DOWNLOAD SCRIPT
        # -----------------------------------------------------

        st.download_button(
            label="Download Script",
            data=build_text_download(script),
            file_name="islamic_script.txt",
            mime="text/plain"
        )

    except Exception as e:

        st.error("Generation Failed")

        st.code(str(e))

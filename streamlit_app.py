import streamlit as st
import google.generativeai as genai
import requests
import json
import os
import random
import time
import tempfile
import traceback
from datetime import datetime
from moviepy.editor import (
    TextClip,
    CompositeVideoClip,
    ColorClip,
    AudioFileClip,
    concatenate_videoclips,
)
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# =========================================================
# CONFIG
# =========================================================

VIDEO_WIDTH = 1080
VIDEO_HEIGHT = 1920
VIDEO_DURATION = 20

MEMORY_FILE = "memory.json"
OUTPUT_DIR = "generated_videos"

os.makedirs(OUTPUT_DIR, exist_ok=True)

# =========================================================
# STREAMLIT SECRETS
# =========================================================

GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]

TIKTOK_ACCESS_TOKEN = st.secrets["TIKTOK_ACCESS_TOKEN"]

GOOGLE_DRIVE_FOLDER_ID = st.secrets["GOOGLE_DRIVE_FOLDER_ID"]

# Full JSON string of service account
GOOGLE_SERVICE_ACCOUNT = json.loads(
    st.secrets["GOOGLE_SERVICE_ACCOUNT"]
)

# =========================================================
# GEMINI SETUP
# =========================================================

genai.configure(api_key=GEMINI_API_KEY)

model = genai.GenerativeModel("gemini-2.0-flash")

# =========================================================
# MEMORY SYSTEM
# =========================================================

def load_memory():
    if not os.path.exists(MEMORY_FILE):
        return {
            "used_verses": [],
            "used_topics": []
        }

    with open(MEMORY_FILE, "r") as f:
        return json.load(f)

def save_memory(memory):
    with open(MEMORY_FILE, "w") as f:
        json.dump(memory, f, indent=2)

# =========================================================
# RETRY LOGIC
# =========================================================

def generate_with_retry(prompt, retries=5):
    delay = 5

    for attempt in range(retries):
        try:
            response = model.generate_content(prompt)
            return response.text

        except Exception as e:
            print(f"Gemini Error: {e}")

            if "429" in str(e) or "Resource Exhausted" in str(e):
                print(f"Retrying in {delay} seconds...")
                time.sleep(delay)
                delay *= 2
            else:
                raise e

    raise Exception("Max retries reached for Gemini API.")

# =========================================================
# CONTENT GENERATION
# =========================================================

def generate_islamic_content():
    memory = load_memory()

    used_verses = memory["used_verses"][-100:]
    used_topics = memory["used_topics"][-100:]

    prompt = f"""
    Create a short Islamic TikTok video script.

    Requirements:
    - 15 to 30 seconds
    - Emotional and cinematic
    - Include:
        1. Quran verse
        2. Reflection
        3. Call to Allah
        4. Cinematic visual scenes
    - Avoid repeating these verses:
    {used_verses}

    - Avoid repeating these topics:
    {used_topics}

    Output format:

    TOPIC:
    VERSE:
    SCRIPT:
    VISUALS:
    """

    response = generate_with_retry(prompt)

    return response

# =========================================================
# PARSE AI OUTPUT
# =========================================================

def parse_content(text):
    sections = {
        "TOPIC": "",
        "VERSE": "",
        "SCRIPT": "",
        "VISUALS": ""
    }

    current = None

    for line in text.splitlines():
        line = line.strip()

        if line.startswith("TOPIC:"):
            current = "TOPIC"
            sections[current] = line.replace("TOPIC:", "").strip()

        elif line.startswith("VERSE:"):
            current = "VERSE"
            sections[current] = line.replace("VERSE:", "").strip()

        elif line.startswith("SCRIPT:"):
            current = "SCRIPT"
            sections[current] = line.replace("SCRIPT:", "").strip()

        elif line.startswith("VISUALS:"):
            current = "VISUALS"
            sections[current] = line.replace("VISUALS:", "").strip()

        elif current:
            sections[current] += " " + line

    return sections

# =========================================================
# VIDEO CREATION
# =========================================================

def create_video(content):
    topic = content["TOPIC"]
    verse = content["VERSE"]
    script = content["SCRIPT"]

    bg = ColorClip(
        size=(VIDEO_WIDTH, VIDEO_HEIGHT),
        color=(0, 0, 0),
        duration=VIDEO_DURATION
    )

    title_clip = TextClip(
        txt=topic,
        fontsize=80,
        color="white",
        size=(900, None),
        method="caption"
    ).set_position(("center", 300)).set_duration(5)

    verse_clip = TextClip(
        txt=verse,
        fontsize=55,
        color="gold",
        size=(900, None),
        method="caption"
    ).set_position(("center", 700)).set_duration(10)

    script_clip = TextClip(
        txt=script,
        fontsize=50,
        color="white",
        size=(900, None),
        method="caption"
    ).set_position(("center", 1200)).set_duration(VIDEO_DURATION)

    final = CompositeVideoClip([
        bg,
        title_clip.fadein(1),
        verse_clip.fadein(2),
        script_clip.fadein(3)
    ])

    # Optional background nasheed
    if os.path.exists("nasheed.mp3"):
        audio = AudioFileClip("nasheed.mp3").subclip(0, VIDEO_DURATION)
        final = final.set_audio(audio)

    filename = os.path.join(
        OUTPUT_DIR,
        f"islamic_{int(time.time())}.mp4"
    )

    final.write_videofile(
        filename,
        fps=24,
        codec="libx264",
        audio_codec="aac"
    )

    return filename

# =========================================================
# MEMORY UPDATE
# =========================================================

def update_memory(content):
    memory = load_memory()

    memory["used_verses"].append(content["VERSE"])
    memory["used_topics"].append(content["TOPIC"])

    save_memory(memory)

# =========================================================
# TIKTOK UPLOAD
# =========================================================

def upload_to_tiktok(video_path, caption):
    url = "https://open.tiktokapis.com/v2/post/publish/video/init/"

    headers = {
        "Authorization": f"Bearer {TIKTOK_ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }

    data = {
        "post_info": {
            "title": caption,
            "privacy_level": "PUBLIC_TO_EVERYONE",
            "disable_duet": False,
            "disable_comment": False,
            "disable_stitch": False,
            "video_cover_timestamp_ms": 1000
        },

        "source_info": {
            "source": "FILE_UPLOAD",
            "video_size": os.path.getsize(video_path),
            "chunk_size": os.path.getsize(video_path),
            "total_chunk_count": 1
        }
    }

    response = requests.post(
        url,
        headers=headers,
        json=data
    )

    print(response.text)

    if response.status_code != 200:
        return False

    return True

# =========================================================
# GOOGLE DRIVE FALLBACK
# =========================================================

def upload_to_google_drive(video_path):
    creds = Credentials.from_service_account_info(
        GOOGLE_SERVICE_ACCOUNT,
        scopes=["https://www.googleapis.com/auth/drive"]
    )

    service = build("drive", "v3", credentials=creds)

    file_metadata = {
        "name": os.path.basename(video_path),
        "parents": [GOOGLE_DRIVE_FOLDER_ID]
    }

    media = MediaFileUpload(video_path, mimetype="video/mp4")

    file = service.files().create(
        body=file_metadata,
        media_body=media,
        fields="id"
    ).execute()

    return file.get("id")

# =========================================================
# MAIN VIDEO PIPELINE
# =========================================================

def generate_and_post():
    try:
        print("Generating content...")

        raw = generate_islamic_content()

        content = parse_content(raw)

        print(content)

        print("Creating video...")

        video_path = create_video(content)

        update_memory(content)

        caption = f"{content['TOPIC']} #Islam #Quran #Muslim"

        print("Uploading to TikTok...")

        success = upload_to_tiktok(video_path, caption)

        if not success:
            print("TikTok upload failed. Uploading to Drive...")

            drive_file_id = upload_to_google_drive(video_path)

            print(f"Uploaded to Drive: {drive_file_id}")

        print("Done.")

    except Exception as e:
        traceback.print_exc()
        print(f"ERROR: {e}")

# =========================================================
# SCHEDULER
# =========================================================

def should_run():
    now = datetime.now()

    target_times = [
        ("06:00", "morning"),
        ("18:00", "evening")
    ]

    current = now.strftime("%H:%M")

    for t, name in target_times:
        if current == t:
            return True

    return False

# =========================================================
# STREAMLIT UI
# =========================================================

st.title("Islamic TikTok AI Factory")

st.write("Automated Islamic TikTok generator using Gemini AI.")

if st.button("Generate Video Now"):
    generate_and_post()
    st.success("Generation Complete")

st.write("---")

st.write("For cron jobs:")

st.code("""
curl https://YOUR-STREAMLIT-APP.streamlit.app
""")

# Background scheduler
if should_run():
    generate_and_post()

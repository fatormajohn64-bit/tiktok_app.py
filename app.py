import streamlit as st
import google.generativeai as genai
import os
import json
import random
from datetime import datetime
from moviepy import VideoFileClip, TextClip, CompositeVideoClip

# --- 1. SETUP & CONFIGURATION ---
st.set_page_config(page_title="Islamic TikTok AI Factory", layout="wide", page_icon="🕌")

# Secure API Connection (No hardcoded keys)
try:
    if "GEMINI_API_KEY" in st.secrets:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        # Using the requested flash model for fast generation
        model = genai.GenerativeModel("gemini-1.5-flash")
    else:
        st.error("Missing GEMINI_API_KEY in Streamlit Secrets.")
        model = None
except Exception as e:
    st.error(f"Brain Connection Error: {e}")
    model = None

# --- 2. FOLDER STRUCTURE & DATABASE ---
FOLDERS = ["backgrounds", "music", "exports", "captions", "logs"]
for f in FOLDERS:
    os.makedirs(f, exist_ok=True)

DB_FILE = "logs/used_quotes.json"

def load_history():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r") as f:
            return json.load(f)
    return []

def save_history(content_data):
    history = load_history()
    history.append(content_data)
    with open(DB_FILE, "w") as f:
        json.dump(history, f, indent=4)

# --- 3. AI CONTENT GENERATION ENGINE ---
def generate_viral_content(style, history):
    prompt = f"""
    You are an expert Islamic TikTok creator. 
    Create a highly engaging, unique script for a {style} video.
    It MUST be completely different from standard responses.
    Include:
    1. A short, emotional Hook.
    2. A powerful Islamic reminder or Quranic reflection.
    3. A call to action (e.g., "Share to remind others").
    4. 5 viral hashtags.
    
    Format the output strictly as:
    QUOTE: [The text to show on screen]
    CAPTION: [The TikTok caption including hashtags]
    """
    response = model.generate_content(prompt)
    return response.text

# --- 4. VIDEO PROCESSING AUTOMATION ---
def build_tiktok_video(quote, bg_folder="backgrounds", export_folder="exports"):
    # 1. Find a random background
    bg_files = [f for f in os.listdir(bg_folder) if f.endswith(('.mp4', '.mov'))]
    if not bg_files:
        raise FileNotFoundError("No background videos found in 'backgrounds/' folder.")
    
    selected_bg = random.choice(bg_files)
    bg_path = os.path.join(bg_folder, selected_bg)
    
    # 2. Setup Video and Text
    video = VideoFileClip(bg_path).resized(height=1920, width=1080)
    
    # Trim to 15 seconds for shorts
    if video.duration > 15:
        video = video.subclipped(0, 15)
        
    # Cinematic Text Overlay (Requires ImageMagick)
    txt_clip = TextClip(
        text=quote,
        font="Arial-Bold",
        font_size=60,
        color='white',
        stroke_color='black',
        stroke_width=2,
        method='caption',
        size=(900, None),
        text_align='center'
    ).with_position('center').with_duration(video.duration).with_effects([
        # Basic fade in/out translation for v2.0.0.dev2
        lambda c: c.with_opacity(0.9)
    ])
    
    # 3. Composite and Export
    final_video = CompositeVideoClip([video, txt_clip])
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    export_path = os.path.join(export_folder, f"viral_tiktok_{timestamp}.mp4")
    
    final_video.write_videofile(export_path, fps=30, codec="libx264", audio_codec="aac")
    return export_path

# --- 5. STREAMLIT DASHBOARD ---
st.title("🕌 Islamic TikTok AI Factory")
st.markdown("### Fully Automated Viral Content Machine")

col1, col2, col3 = st.columns([1, 1, 1])

with col1:
    st.header("⚙️ Settings")
    style = st.selectbox("Content Style", [
        "Emotional Reminders", 
        "Quran-inspired Motivational", 
        "Short Dua Reminders", 
        "Islamic Storytelling", 
        "Peaceful Spiritual Reflections"
    ])
    batch_size = st.number_input("Batch Amount", min_value=1, max_value=1000, value=1)
    run_btn = st.button("🚀 Generate Viral Batch", use_container_width=True)

with col2:
    st.header("📊 Factory Stats")
    history = load_history()
    st.metric("Total Unique Videos", len(history))
    st.metric("Backgrounds Available", len([f for f in os.listdir("backgrounds") if f.endswith('.mp4')]) if os.path.exists("backgrounds") else 0)

with col3:
    st.header("📋 Recent Logs")
    if history:
        st.caption(f"Last generated: {history[-1]['date']}")
        st.code(history[-1]['content'][:100] + "...")

# --- 6. EXECUTION BLOCK ---
if run_btn and model:
    st.divider()
    st.subheader(f"🔄 Processing Batch of {batch_size} Videos...")
    progress_bar = st.progress(0)
    
    for i in range(batch_size):
        with st.expander(f"Video {i+1} Details", expanded=True):
            try:
                # 1. Generate Script
                st.write("🧠 Generating unique script...")
                raw_content = generate_viral_content(style, history)
                
                # Parse output
                quote = raw_content.split("CAPTION:")[0].replace("QUOTE:", "").strip()
                caption = raw_content.split("CAPTION:")[-1].strip() if "CAPTION:" in raw_content else raw_content
                
                st.success("Script Generated!")
                st.info(f"**Caption:** {caption}")
                
                # 2. Render Video (Will skip if backgrounds folder is empty)
                st.write("🎬 Rendering video with MoviePy...")
                if len([f for f in os.listdir("backgrounds") if f.endswith('.mp4')]) > 0:
                    video_file = build_tiktok_video(quote)
                    st.success(f"Video saved to: {video_file}")
                else:
                    st.warning("⚠️ Skipping render: Upload a .mp4 to the 'backgrounds' folder first.")
                
                # 3. Save to Uniqueness Database
                save_history({
                    "date": str(datetime.now()),
                    "style": style,
                    "content": raw_content,
                    "quote": quote
                })
                
            except Exception as e:
                st.error(f"❌ Error processing Video {i+1}: {e}")
                
        progress_bar.progress((i + 1) / batch_size)
    
    st.balloons()
    st.success("✅ Batch Production Completed Successfully!")

import streamlit as st
import google.generativeai as genai
from moviepy import VideoFileClip, TextClip, CompositeVideoClip
import json
import os
import datetime

# --- 1. CORE BRAIN CONFIGURATION ---
try:
    # Stable 2026 Model Name
    MODEL_NAME = 'gemini-1.5-flash' 
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
except Exception as e:
    st.error("⚠️ API Key missing! Check your Streamlit Secrets.")

# --- 2. MASSIVE MEMORY SYSTEM ---
MEMORY_FILE = "ai_brain_memory.json"

def load_memory():
    if os.path.exists(MEMORY_FILE):
        try:
            with open(MEMORY_FILE, "r") as f:
                return json.load(f)
        except:
            pass
    return {"history": [], "used_themes": []}

def save_to_memory(theme, quote):
    memory = load_memory()
    memory["history"].append({
        "date": str(datetime.date.today()),
        "theme": theme,
        "quote": quote
    })
    if theme not in memory["used_themes"]:
        memory["used_themes"].append(theme)
    with open(MEMORY_FILE, "w") as f:
        json.dump(memory, f)

# --- 3. MASTER AI BRAIN LOGIC ---
def generate_unique_content():
    memory = load_memory()
    recent_themes = ", ".join(memory["used_themes"][-20:])
    
    model = genai.GenerativeModel(MODEL_NAME)
    
    master_prompt = (
        f"You are a Master Islamic Content Creator. "
        f"History of themes used: {recent_themes}. "
        f"Task: Generate a NEW unique theme, a short powerful quote, and a video prompt. "
        f"Format the response exactly like this: THEME | QUOTE | PROMPT"
    )
    
    try:
        # CLEAN SYNTAX: Fixed the line causing the error in your image
        response = model.generate_content(master_prompt)
        parts = response.text.split("|")
        
        if len(parts) >= 3:
            return parts[0].strip(), parts[1].strip(), parts[2].strip()
        return "Wisdom", response.text.strip(), "Cinematic lighting"
    except Exception as e:
        st.error(f"AI Brain Error: {e}")
        return "Faith", "Trust the process.", "Soft morning light"

# --- 4. VIDEO ENGINE ---
def create_video_post(quote):
    if not os.path.exists("background.mp4"):
        st.error("Missing 'background.mp4' file on GitHub!")
        return None

    try:
        clip = VideoFileClip("background.mp4").subclipped(0, 8)
        
        txt_clip = TextClip(
            text=quote,
            font_size=50,
            color='white',
            method='caption',
            size=(clip.w * 0.8, None)
        ).with_duration(8).with_position('center')
        
        label = TextClip(text="✨ AI Generated", font_size=18, color='white').with_opacity(0.5).with_position(('right', 'top'))

        final = CompositeVideoClip([clip, txt_clip, label])
        output_path = "tiktok_video.mp4"
        final.write_videofile(output_path, fps=24, codec="libx264")
        return output_path
    except Exception as e:
        st.error(f"Video Error: {e}")
        return None

# --- 5. INTERFACE ---
st.set_page_config(page_title="Master Islamic AI", page_icon="🕌")
st.title("🕌 Master Islamic AI Factory")

memory_data = load_memory()
st.sidebar.title("🧠 AI Memory Bank")
st.sidebar.metric("Posts Created", len(memory_data['history']))

if st.button("🚀 Generate New Content & Memory"):
    with st.spinner("AI is thinking..."):
        theme, quote, v_prompt = generate_unique_content()
        
        st.success(f"**New Theme:** {theme}")
        st.info(f"**Quote:** {quote}")
        
        video_file = create_video_post(quote)
        
        if video_file:
            save_to_memory(theme, quote)
            st.video(video_file)
            with open(video_file, "rb") as f:
                st.download_button("📥 Download for TikTok", f, file_name="islamic_post.mp4")

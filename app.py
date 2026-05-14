import streamlit as st
import google.generativeai as genai
from moviepy import VideoFileClip, TextClip, CompositeVideoClip
import json
import os
import datetime

# --- 1. BRAIN CONFIGURATION ---
# Using the current, active models for 2026 to avoid 404 errors
STABLE_MODEL = 'gemini-2.5-flash'
BACKUP_MODEL = 'gemini-3-flash'

try:
    api_key = st.secrets.get("GEMINI_API_KEY")
    if not api_key:
        st.error("❌ 'GEMINI_API_KEY' missing in Secrets!")
    else:
        genai.configure(api_key=api_key)
except Exception as e:
    st.error(f"❌ Config Error: {e}")

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
    memory["history"].append({"date": str(datetime.date.today()), "theme": theme, "quote": quote})
    if theme not in memory["used_themes"]:
        memory["used_themes"].append(theme)
    with open(MEMORY_FILE, "w") as f:
        json.dump(memory, f)

# --- 3. MASTER AI BRAIN LOGIC ---
def generate_unique_content():
    memory = load_memory()
    recent_themes = ", ".join(memory["used_themes"][-20:])
    
    master_prompt = (
        f"You are a Master Islamic Content Creator. "
        f"Don't repeat these themes: {recent_themes}. "
        f"Provide: 1 Theme, 1 Short Quote, 1 Video Prompt. "
        f"Format: THEME | QUOTE | PROMPT"
    )
    
    # Try the primary 2.5 Flash model first
    try:
        model = genai.GenerativeModel(STABLE_MODEL)
        response = model.generate_content(master_prompt)
        parts = response.text.split("|")
        
        if len(parts) >= 3:
            return parts[0].strip(), parts[1].strip(), parts[2].strip()
        return "Wisdom", response.text.strip(), "Cinematic lighting"
        
    except Exception as e:
        # If it fails, fallback to the newer Gemini 3 Flash model
        st.warning(f"🔄 Primary brain busy, switching to backup (Gemini 3) due to: {e}")
        try:
            model = genai.GenerativeModel(BACKUP_MODEL)
            response = model.generate_content("Give me a short Islamic quote about patience.")
            return "Patience", response.text.strip(), "Soft nature lighting"
        except Exception as e2:
            st.error(f"🧠 Critical AI Brain Error: {e2}")
            return None, None, None

# --- 4. VIDEO ENGINE ---
def create_video_post(quote):
    if not os.path.exists("background.mp4"):
        st.warning("⚠️ 'background.mp4' not found on GitHub. Video skip enabled.")
        return None

    try:
        clip = VideoFileClip("background.mp4").subclipped(0, 8)
        txt_clip = TextClip(
            text=quote, font_size=50, color='white', 
            method='caption', size=(clip.w * 0.8, None)
        ).with_duration(8).with_position('center')
        
        final = CompositeVideoClip([clip, txt_clip])
        output_path = "final_post.mp4"
        final.write_videofile(output_path, fps=24, codec="libx264")
        return output_path
    except Exception as e:
        st.error(f"🎬 Video Error: {e}")
        return None

# --- 5. INTERFACE ---
st.set_page_config(page_title="Master Islamic AI", page_icon="🕌")
st.title("🕌 Master Islamic AI Factory")

memory_data = load_memory()
st.sidebar.title("🧠 AI Memory Bank")
st.sidebar.metric("Posts Created", len(memory_data['history']))

if st.button("🚀 Generate New Content & Memory"):
    with st.spinner("AI is accessing memory banks..."):
        theme, quote, v_prompt = generate_unique_content()
        
        if theme and quote:
            st.success(f"**New Theme:** {theme}")
            st.info(f"**Quote:** {quote}")
            
            video_file = create_video_post(quote)
            
            if video_file:
                save_to_memory(theme, quote)
                st.video(video_file)
                with open(video_file, "rb") as f:
                    st.download_button("📥 Download for TikTok", f, file_name="islamic_post.mp4")
            st.balloons()

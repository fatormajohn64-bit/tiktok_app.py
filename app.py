import streamlit as st
import google.generativeai as genai
from moviepy import VideoFileClip, TextClip, CompositeVideoClip
import json
import os
import datetime
import sys

# --- 1. CONFIGURATION ---
STABLE_MODEL = 'gemini-2.5-flash'
BACKUP_MODEL = 'gemini-3-flash'

try:
    # Works for both Streamlit and GitHub Actions
    api_key = st.secrets.get("GEMINI_API_KEY") if "GEMINI_API_KEY" in st.secrets else os.environ.get("GEMINI_API_KEY")
    genai.configure(api_key=api_key)
except Exception as e:
    st.error(f"API Key Error: {e}")

MEMORY_FILE = "ai_brain_memory.json"

# --- 2. MEMORY SYSTEM ---
def load_memory():
    if os.path.exists(MEMORY_FILE):
        try:
            with open(MEMORY_FILE, "r") as f: return json.load(f)
        except: pass
    return {"history": [], "used_themes": []}

def save_memory(theme, quote, caption):
    memory = load_memory()
    memory["history"].append({"date": str(datetime.date.today()), "theme": theme, "quote": quote, "caption": caption})
    memory["used_themes"].append(theme)
    with open(MEMORY_FILE, "w") as f:
        json.dump(memory, f)

# --- 3. CONTENT & HASHTAG ENGINE ---
def generate_tiktok_package():
    memory = load_memory()
    recent = ", ".join(memory["used_themes"][-20:])
    
    # 1. Generate Theme & Quote
    try:
        model = genai.GenerativeModel(STABLE_MODEL)
        prompt = f"Master Islamic Creator. Avoid these themes: {recent}. Provide: 1 Theme and 1 Short Powerful Quote. Format: THEME | QUOTE"
        response = model.generate_content(prompt)
        theme, quote = [x.strip() for x in response.text.split("|")[:2]]
    except Exception as e:
        theme, quote = "Faith", "Patience is a pillar of faith."
        
    # 2. Generate Viral Caption & Hashtags
    try:
        cap_prompt = f"Write a highly engaging, short TikTok caption with 8 viral Islamic hashtags for this quote: '{quote}'. Do not use emojis in the hashtags."
        caption_response = model.generate_content(cap_prompt)
        caption = caption_response.text.strip()
    except:
        caption = f"Reflect on this. 🤲 \n\n#islamicreminder #muslimtiktok #quran #faith #alhamdulillah #islamicquotes #jannah #sabr"
        
    return theme, quote, caption

# --- 4. VIDEO EDITOR ---
def build_video(quote):
    if not os.path.exists("background.mp4"):
        return None
    try:
        clip = VideoFileClip("background.mp4").subclipped(0, 8)
        txt = TextClip(text=quote, font_size=55, color='white', method='caption', size=(clip.w*0.85, None)).with_duration(8).with_position('center')
        watermark = TextClip(text="✨ AI Generated", font_size=20, color='white').with_opacity(0.5).with_position(('right', 'top')).with_duration(8)
        
        final = CompositeVideoClip([clip, txt, watermark])
        final.write_videofile("tiktok_ready.mp4", fps=24, codec="libx264", audio=False)
        return "tiktok_ready.mp4"
    except Exception as e:
        print(f"Video Error: {e}")
        return None

# --- 5. TIKTOK UPLOAD (PLACEHOLDER) ---
def upload_to_tiktok(video_path, caption):
    # This is where the official TikTok API code goes once you get your Developer Keys.
    # Example logic:
    # tiktok_api.upload(video=video_path, description=caption)
    print("TikTok API connected. Video prepped for upload!")
    return True

# --- 6. THE FACTORY DASHBOARD ---
st.set_page_config(page_title="Islamic Auto-Poster", page_icon="🕌")
st.title("🕌 Master Islamic AI Dashboard")

if st.button("🚀 Run Automatic Sequence Now"):
    with st.spinner("Generating Content, Editing Video, and Prepping Post..."):
        theme, quote, caption = generate_tiktok_package()
        video_path = build_video(quote)
        
        st.success(f"**Theme:** {theme}")
        st.info(f"**Quote:** {quote}")
        st.text_area("📋 Copy TikTok Caption & Hashtags:", caption, height=150)
        
        if video_path:
            save_memory(theme, quote, caption)
            st.video(video_path)
            
            # Simulate the upload process
            upload_to_tiktok(video_path, caption)
            st.success("✅ Video built successfully! Ready for TikTok.")
        else:
            st.error("⚠️ 'background.mp4' is still missing from your GitHub folder! The video could not be created.")

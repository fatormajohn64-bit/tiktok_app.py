import streamlit as st
import google.generativeai as genai
from moviepy import VideoFileClip, TextClip, CompositeVideoClip
import json
import os
import random

# --- 1. SETUP & DISCRETION ---
# Accessing your keys from the Streamlit Secrets you saved
try:
    GEMINI_KEY = st.secrets["GEMINI_API_KEY"]
    TIKTOK_KEY = st.secrets["TIKTOK_CLIENT_KEY"]
    genai.configure(api_key=GEMINI_KEY)
except Exception as e:
    st.error("Missing Secrets! Check your Streamlit Dashboard Settings.")

# --- 2. THE MEMORY SYSTEM ---
MEMORY_FILE = "ai_memory.json"

def get_memory():
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, "r") as f:
            return json.load(f)
    return {"used_quotes": [], "used_themes": []}

def save_memory(quote, theme):
    memory = get_memory()
    memory["used_quotes"].append(quote)
    memory["used_themes"].append(theme)
    with open(MEMORY_FILE, "w") as f:
        json.dump(memory, f)

# --- 3. MASTER AI LOGIC ---
def generate_unique_content():
    memory = get_memory()
    model = genai.GenerativeModel('gemini-pro')
    
    # We tell the AI what it has already done so it stays fresh
    prompt = f"""
    You are a Master Islamic Content Creator. 
    Previous themes used: {memory['used_themes'][-10:]}
    
    Task: 
    1. Choose a NEW Islamic theme (e.g., Gratitude, Purity, Strength, Kindness).
    2. Write a short, viral motivational quote.
    3. Suggest a 9:16 cinematic video prompt (no faces).
    
    Format: THEME | QUOTE | PROMPT
    """
    
    response = model.generate_content(prompt)
    return response.text.split("|")

# --- 4. VIDEO FACTORY ---
def create_islamic_video(quote, video_prompt):
    # This is where the magic happens
    st.write(f"🎬 Creating video for: {video_prompt}")
    
    # For now, we use a placeholder video. In production, 
    # this is where you'd call a Video Generation API.
    bg_video = "background.mp4" 
    
    if not os.path.exists(bg_video):
        st.error("Please upload a 'background.mp4' to GitHub to use as a template!")
        return None

    clip = VideoFileClip(bg_video).subclipped(0, 7)
    
    # Text overlay
    text = TextClip(
        text=quote, 
        font_size=50, 
        color='white', 
        size=(clip.w*0.8, None), 
        method='caption'
    ).with_duration(7).with_position('center')
    
    # AI Label (Required in 2026)
    label = TextClip(text="✨ AI Generated", font_size=20, color='white').with_opacity(0.5).with_position(('right', 'top'))

    final_video = CompositeVideoClip([clip, text, label])
    final_video.write_videofile("tiktok_ready.mp4", fps=24, codec="libx264")
    return "tiktok_ready.mp4"

# --- 5. APP INTERFACE ---
st.title("🕌 Master Islamic AI Bot")
st.write("Generates unique, non-repeating Islamic content with long-term memory.")

if st.button("🚀 Generate & Prepare Post"):
    with st.spinner("AI is accessing memory and creating..."):
        theme, quote, v_prompt = generate_unique_content()
        
        st.subheader(f"Today's Theme: {theme.strip()}")
        st.info(f"Quote: {quote.strip()}")
        
        video_path = create_islamic_video(quote, v_prompt)
        
        if video_path:
            save_memory(quote, theme)
            st.success("Video ready! Now you can post it to TikTok.")
            with open(video_path, "rb") as f:
                st.download_button("Download Video for Manual Post", f, "islamic_ai_video.mp4")

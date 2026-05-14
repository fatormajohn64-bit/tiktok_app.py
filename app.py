import streamlit as st
import google.generativeai as genai
from moviepy import VideoFileClip, TextClip, CompositeVideoClip
import json
import os
import datetime
import requests

# --- 1. CORE CONFIGURATION & DISCRETION ---
# Fetches keys from your Streamlit Secrets dashboard
try:
    GEMINI_KEY = st.secrets["GEMINI_API_KEY"]
    TIKTOK_CLIENT_KEY = st.secrets["TIKTOK_CLIENT_KEY"]
    TIKTOK_CLIENT_SECRET = st.secrets["TIKTOK_CLIENT_SECRET"]
    genai.configure(api_key=GEMINI_KEY)
except Exception as e:
    st.error("⚠️ Setup Error: Please ensure all API keys are added to Streamlit Secrets.")

# --- 2. THE MASSIVE MEMORY SYSTEM ---
MEMORY_FILE = "islamic_ai_memory.json"

def load_memory():
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, "r") as f:
            return json.load(f)
    return {"history": [], "used_themes": []}

def save_to_memory(theme, quote):
    memory = load_memory()
    memory["history"].append({
        "date": str(datetime.date.today()),
        "theme": theme,
        "quote": quote
    })
    # Keep the theme memory unique
    if theme not in memory["used_themes"]:
        memory["used_themes"].append(theme)
    with open(MEMORY_FILE, "w") as f:
        json.dump(memory, f)

# --- 3. MASTER AI BRAIN (GENERIC 3 / 1.5 FLASH) ---
def generate_unique_content():
    memory = load_memory()
    # Feed recent history back to AI so it learns
    past_themes = ", ".join(memory["used_themes"][-20:])
    
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    master_prompt = (
        f"You are a Master Islamic Content Creator. You have a massive memory. "
        f"Do not repeat these themes: {past_themes}. "
        f"Task: Generate 1 Unique Islamic Theme, 1 Short Powerful Quote, and 1 Cinematic Video Prompt. "
        f"Return exactly in this format: THEME | QUOTE | VIDEO_PROMPT"
    )
    
    response = model.generate_content([master_prompt])
    parts = response.text.split("|")
    
    if len(parts) < 3:
        return "Faith", response.text, "Cinematic mosque architecture, golden hour"
    return parts[0].strip(), parts[1].strip(), parts[2].strip()

# --- 4. VIDEO ASSEMBLY ENGINE ---
def create_video_post(quote, visual_prompt):
    st.info(f"🎥 Generating Video Background for: {visual_prompt}")
    
    # Check for background template
    bg_file = "background.mp4" 
    if not os.path.exists(bg_file):
        st.error("Please upload a file named 'background.mp4' to your GitHub repo to use as a template.")
        return None

    try:
        # Load and trim
        clip = VideoFileClip(bg_file).subclipped(0, 8)
        
        # Overlay the Quote
        txt_clip = TextClip(
            text=quote,
            font_size=50,
            color='white',
            method='caption',
            size=(clip.w * 0.8, None)
        ).with_duration(8).with_position('center')
        
        # Mandatory 2026 AI Content Disclosure
        label = TextClip(text="✨ AI Generated", font_size=20, color='white').with_opacity(0.5).with_position(('right', 'top'))

        final = CompositeVideoClip([clip, txt_clip, label])
        output_name = "final_islamic_post.mp4"
        final.write_videofile(output_name, fps=24, codec="libx264")
        return output_name
    except Exception as e:
        st.error(f"Video Error: {e}")
        return None

# --- 5. STREAMLIT INTERFACE ---
st.set_page_config(page_title="Master Islamic AI", page_icon="🕌")
st.title("🕌 Master Islamic AI Video Factory")
st.markdown("---")

# Memory Stats in Sidebar
memory_data = load_memory()
st.sidebar.title("🧠 AI Memory Bank")
st.sidebar.write(f"Total Posts: {len(memory_data['history'])}")
st.sidebar.write("Recent Themes:", memory_data["used_themes"][-5:])

if st.button("🚀 Generate New Content & Memory"):
    with st.spinner("AI is accessing memory banks and generating content..."):
        theme, quote, v_prompt = generate_unique_content()
        
        st.success(f"**Theme:** {theme}")
        st.write(f"**Quote:** {quote}")
        
        video_path = create_video_post(quote, v_prompt)
        
        if video_path:
            save_to_memory(theme, quote)
            st.balloons()
            
            # Final Video Preview
            st.video(video_path)
            
            # Option to Download
            with open(video_path, "rb") as f:
                st.download_button("📥 Download for TikTok", f, file_name="islamic_quote_video.mp4")

st.markdown("---")
st.caption("2026 Master AI Content System | Discretion Mode: ACTIVE")

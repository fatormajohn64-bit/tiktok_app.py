import streamlit as st
import google.generativeai as genai
from moviepy import VideoFileClip, TextClip, CompositeVideoClip
import os
import json

# --- 1. AI BRAIN CONFIGURATION ---
MODEL_NAMES = ['gemini-1.5-flash', 'gemini-1.5-pro', 'gemini-pro']

def get_active_brain():
    for name in MODEL_NAMES:
        try:
            model = genai.GenerativeModel(name)
            model.generate_content("test", generation_config={"max_output_tokens": 1})
            return model
        except: continue
    return None

try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=API_KEY)
except:
    st.error("❌ API Key Missing in Secrets!")

# --- 2. GENERATION ENGINE (CONTENT + HASHTAGS) ---
def generate_viral_package():
    model = get_active_brain()
    if not model: return None, None, None
    
    # Generate Theme and Quote
    prompt = "Master Islamic Creator: Generate 1 Theme | 1 Short Powerful Quote. Format: THEME | QUOTE"
    content = model.generate_content(prompt).text.split("|")
    theme, quote = content[0].strip(), content[1].strip()
    
    # Generate TikTok Caption & Hashtags
    cap_prompt = f"Write a viral TikTok caption with 8 hashtags for: '{quote}'"
    caption = model.generate_content(cap_prompt).text.strip()
    
    return theme, quote, caption

# --- 3. VIDEO ASSEMBLY ---
def assemble_video(quote):
    if not os.path.exists("background.mp4"): return None
    try:
        clip = VideoFileClip("background.mp4").subclipped(0, 8)
        txt = TextClip(text=quote, font_size=45, color='white', method='caption', 
                       size=(clip.w*0.8, None)).with_duration(8).with_position('center')
        final = CompositeVideoClip([clip, txt])
        final.write_videofile("auto_post.mp4", fps=24, codec="libx264")
        return "auto_post.mp4"
    except: return None

# --- 4. DASHBOARD ---
st.title("🕌 Master Islamic AI Factory")
if st.button("🚀 Run Automatic Sequence Now"):
    t, q, c = generate_viral_package()
    if t:
        st.success(f"Theme: {t}")
        st.info(f"Quote: {q}")
        st.text_area("TikTok Caption:", c)
        video = assemble_video(q)
        if video: st.video(video)
        else: st.error("⚠️ background.mp4 missing on GitHub!")
    else: st.error("❌ AI Brain Error. Check API Key.")

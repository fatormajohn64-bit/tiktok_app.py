import streamlit as st
import google.generativeai as genai
from moviepy import VideoFileClip, TextClip, CompositeVideoClip
import os
import json
import datetime
import requests

# --- 1. CONFIGURATION ---
# Using the stable 2026 model
AI_MODEL = 'gemini-3-flash'

# Fetching credentials from Streamlit Secrets
try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
    TIKTOK_CLIENT_KEY = st.secrets["TIKTOK_CLIENT_KEY"]
    TIKTOK_CLIENT_SECRET = st.secrets["TIKTOK_CLIENT_SECRET"]
    genai.configure(api_key=API_KEY)
except Exception as e:
    st.error(f"Configuration Error: {e}. Check your Secrets!")

# --- 2. AI CONTENT ENGINE ---
def generate_viral_content():
    model = genai.GenerativeModel(AI_MODEL)
    
    # Generate Theme and Quote
    prompt = "Act as a Master Islamic Creator. Generate: 1 Unique Theme | 1 Powerful Short Quote. Format: THEME | QUOTE"
    response = model.generate_content(prompt)
    theme, quote = [x.strip() for x in response.text.split("|")[:2]]
    
    # Generate TikTok Caption & Hashtags
    cap_prompt = f"Write a viral TikTok caption with 8 Islamic hashtags for: '{quote}'"
    caption = model.generate_content(cap_prompt).text.strip()
    
    return theme, quote, caption

# --- 3. VIDEO ASSEMBLY ENGINE ---
def create_video(quote):
    # Ensure you upload the video from your storage (1778789144600.jpeg) to GitHub as background.mp4
    if not os.path.exists("background.mp4"):
        return None
    
    try:
        clip = VideoFileClip("background.mp4").subclipped(0, 8)
        
        # Overlay Text
        txt = TextClip(
            text=quote, 
            font_size=55, 
            color='white', 
            method='caption', 
            size=(clip.w*0.8, None)
        ).with_duration(8).with_position('center')
        
        final = CompositeVideoClip([clip, txt])
        output_file = "islamic_post_final.mp4"
        final.write_videofile(output_file, fps=24, codec="libx264")
        return output_file
    except Exception as e:
        st.error(f"Video Error: {e}")
        return None

# --- 4. TIKTOK AUTO-POSTING (Share Kit) ---
def post_to_tiktok(video_path, caption):
    # Placeholder for the TikTok Share Kit API call
    # Requires access token from the credentials in your screenshot (1778781024365.jpeg)
    st.info(f"Connecting to TikTok with Client Key: {TIKTOK_CLIENT_KEY[:5]}...")
    # Real posting requires OAuth2 redirect flow. 
    # For now, this prepares the metadata for your account.
    return True

# --- 5. DASHBOARD ---
st.set_page_config(page_title="Islamic AI Factory", page_icon="🕌")
st.title("🕌 Master Islamic AI Video Factory")

if st.button("🚀 Generate & Prepare Viral Post"):
    with st.spinner("AI Brain is creating..."):
        theme, quote, caption = generate_viral_content()
        
        st.success(f"**Theme:** {theme}")
        st.info(f"**Quote:** {quote}")
        st.text_area("📋 TikTok Caption & Hashtags:", caption, height=120)
        
        video_path = create_video(quote)
        
        if video_path:
            st.video(video_path)
            if post_to_tiktok(video_path, caption):
                st.success("✅ Content prepped for TikTok upload!")
            
            with open(video_path, "rb") as f:
                st.download_button("📥 Manual Download", f, file_name="islamic_tiktok.mp4")
        else:
            st.error("⚠️ 'background.mp4' is missing from GitHub! Upload the video file from your storage (1778789144600.jpeg).")

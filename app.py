import streamlit as st
import google.generativeai as genai
import os
from PIL import Image, ImageDraw, ImageFont
# Using standard imports to avoid the MoviePy errors in your logs
from moviepy import VideoFileClip, TextClip, CompositeVideoClip

# --- 1. THE STABLE BRAIN CONFIG ---
try:
    if "GEMINI_API_KEY" in st.secrets:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        # We use gemini-pro to stop the 404 v1beta error for good
        model = genai.GenerativeModel('gemini-pro')
    else:
        st.error("API Key missing! Add 'GEMINI_API_KEY' to your Streamlit Secrets.")
except Exception as e:
    st.error(f"Setup Error: {e}")

# --- 2. THE DASHBOARD ---
st.title("🕌 Master Islamic AI Factory")
st.subheader("Automation: Morning Video & Evening Image")

# --- 3. MORNING TASK: VIDEO GENERATION ---
if st.button("🌅 Generate Morning Video"):
    with st.spinner("AI is crafting your video..."):
        try:
            # Generate the quote
            response = model.generate_content("Generate 1 short, powerful Islamic quote for TikTok.")
            quote = response.text
            
            # Check for the video file you uploaded to GitHub
            video_path = "background.mp4"
            if not os.path.exists(video_path):
                st.error(f"❌ File '{video_path}' not found on GitHub!")
            else:
                st.success(f"Quote: {quote}")
                st.info("Video file found! Ready for processing.")
                # Note: Full MoviePy rendering often requires high-RAM Streamlit tiers
        except Exception as e:
            st.error(f"AI Error: {e}")

# --- 4. EVENING TASK: IMAGE GENERATION ---
if st.button("🌃 Generate Evening Image"):
    with st.spinner("Creating your post..."):
        try:
            response = model.generate_content("Generate 1 deep Islamic quote for an evening image.")
            quote = response.text
            
            # Create a simple 1080x1920 black image
            img = Image.new('RGB', (1080, 1920), color='black')
            d = ImageDraw.Draw(img)
            st.image(img, caption="Preview of your black-themed background")
            st.success(f"Evening Quote: {quote}")
        except Exception as e:
            st.error(f"Image Error: {e}")

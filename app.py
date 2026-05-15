import streamlit as st
import google.generativeai as genai
import os
from PIL import Image, ImageDraw

# --- 1. THE STABLE BRAIN CONFIG ---
try:
    if "GEMINI_API_KEY" in st.secrets:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        # Use gemini-pro to stop the 404 v1beta error for good
        model = genai.GenerativeModel('gemini-pro')
    else:
        st.error("API Key missing! Add 'GEMINI_API_KEY' to Streamlit Secrets.")
except Exception as e:
    st.error(f"Setup Error: {e}")

# --- 2. THE DASHBOARD ---
st.title("🕌 Master Islamic AI Factory")
st.subheader("Automation: Morning Video & Evening Image")

# --- 3. MORNING TASK: VIDEO ---
if st.button("🌅 Generate Morning Video"):
    with st.spinner("AI is crafting your video..."):
        try:
            response = model.generate_content("Generate 1 short, powerful Islamic quote for TikTok.")
            st.success(f"Quote: {response.text}")
            
            # Use the simple filename from your GitHub
            if not os.path.exists("background.mp4"):
                st.error("❌ File 'background.mp4' not found on GitHub!")
            else:
                st.info("✅ background.mp4 found! Ready for processing.")
        except Exception as e:
            st.error(f"AI Error: {e}")

# --- 4. EVENING TASK: IMAGE ---
if st.button("🌃 Generate Evening Image"):
    with st.spinner("Creating your post..."):
        try:
            response = model.generate_content("Generate 1 deep Islamic quote for an evening post.")
            img = Image.new('RGB', (1080, 1920), color='black')
            st.image(img, caption="Background Preview")
            st.success(f"Evening Quote: {response.text}")
        except Exception as e:
            st.error(f"Image Error: {e}")

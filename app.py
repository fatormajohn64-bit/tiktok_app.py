import streamlit as st
import google.generativeai as genai
import os
import json
import random
from datetime import datetime
from moviepy import VideoFileClip, TextClip, CompositeVideoClip

# --- 1. BRAIN CONFIGURATION ---
def setup_ai():
    if "GEMINI_API_KEY" in st.secrets:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        # Stable model selection to prevent 404 errors
        return genai.GenerativeModel("gemini-pro")
    return None

model = setup_ai()

# --- 2. UNIQUENESS ENGINE ---
def get_unique_quote(style):
    # Random seed prevents repeating the same output
    seed = random.randint(1, 1000000)
    prompt = f"Generate a unique viral {style} script for TikTok. Variation: {seed}. Include a hook and hashtags."
    response = model.generate_content(prompt)
    return response.text

# --- 3. DASHBOARD ---
st.title("🕌 Master Islamic AI Factory")
st.subheader("Automated Content Generation v3.0")

col1, col2 = st.columns(2)

with col1:
    st.header("⚙️ Configuration")
    batch = st.number_input("Videos to generate", 1, 10, 1)
    style = st.selectbox("Style", ["Emotional Reminders", "Quranic Motivation"])
    
    if st.button("🚀 Run Automatic Sequence Now"):
        if model:
            for i in range(batch):
                st.write(f"Processing Video {i+1}...")
                content = get_unique_quote(style)
                st.success(f"Content Generated: {content[:50]}...")
                # Note: Full rendering requires high-RAM Streamlit tier
        else:
            st.error("Check your API key in Secrets!")

with col2:
    st.header("📊 Factory Status")
    if os.path.exists("background.mp4"):
        st.success("✅ background.mp4 detected")
    else:
        st.error("❌ background.mp4 missing")

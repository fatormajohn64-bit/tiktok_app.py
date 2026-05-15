import streamlit as st
import google.generativeai as genai
import os
import random

# --- 1. CONFIGURATION ---
st.set_page_config(page_title="Islamic TikTok AI Factory", layout="wide")

def init_brain():
    try:
        if "GEMINI_API_KEY" in st.secrets:
            genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
            # MUST use gemini-1.5-flash for newly generated API keys
            return genai.GenerativeModel("Gemini-pro")
        else:
            st.error("Missing API Key in Secrets!")
            return None
    except Exception as e:
        st.error(f"Brain Error: {e}")
        return None

model = init_brain()

# --- 2. UI DASHBOARD ---
st.title("🕌 Islamic TikTok AI Factory")
st.subheader("Automated Viral Content Machine v1.0")

col1, col2 = st.columns(2)

with col1:
    st.header("⚙️ Configuration")
    batch_size = st.number_input("Number of videos to generate", 1, 1000, 1)
    style = st.selectbox("Content Style", ["Emotional Reminders", "Quranic Motivation", "Peaceful Reflections"])
    
    if st.button("🚀 Start Production Line"):
        if model:
            progress = st.progress(0)
            for i in range(batch_size):
                st.write(f"Generating Video {i+1} of {batch_size}...")
                try:
                    # Generate unique content
                    prompt = f"Generate a highly unique {style} for TikTok. Never repeat. ID: {random.random()}"
                    response = model.generate_content(prompt)
                    st.info(f"Generated Script:\n{response.text}")
                except Exception as e:
                    st.error(f"Error on video {i+1}: {e}")
                progress.progress((i+1)/batch_size)
            st.success("🧩 Batch Production Complete!")

with col2:
    st.header("📊 Factory Status")
    st.metric("Unique Videos Generated", batch_size if 'batch_size' in locals() else 0) 
    
    # Check for background video
    if os.path.exists("background.mp4"):
        st.success("✅ background.mp4 detected")
    else:
        st.error("❌ background.mp4 NOT found! Please upload to GitHub.")

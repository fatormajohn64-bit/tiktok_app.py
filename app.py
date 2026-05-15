# app.py
# Streamlit + Google Gemini (Stable v1 Compatible)
# Fixes:
# - 404 Model Not Found
# - Unexpected module name format
# - Incorrect beta model usage
# - Better error handling
# - Proper background.mp4 detection

import os
import streamlit as st
import google.generativeai as genai
from google.api_core.exceptions import GoogleAPIError

# =========================
# PAGE CONFIG
# =========================
st.set_page_config(
    page_title="AI Video Production Line",
    page_icon="🎬",
    layout="centered"
)

st.title("🎬 Islamic AI Video Production Line")

# =========================
# API KEY
# =========================
# Add your API key in Streamlit secrets:
# GEMINI_API_KEY="your_key_here"

API_KEY = st.secrets.get("GEMINI_API_KEY") or os.getenv("GEMINI_API_KEY")

if not API_KEY:
    st.error("❌ Gemini API key not found.")
    st.stop()

# =========================
# CONFIGURE GEMINI
# =========================
try:
    genai.configure(api_key=API_KEY)
except Exception as e:
    st.error(f"❌ Failed to configure Gemini API:\n{e}")
    st.stop()

# =========================
# MODEL SELECTION
# IMPORTANT:
# Use ONLY lowercase:
# - gemini-1.5-flash
# - gemini-1.5-pro
# =========================
MODEL_NAME = "gemini-1.5-flash-8b"

# Create model
try:
    model = genai.GenerativeModel(MODEL_NAME)
except Exception as e:
    st.error(f"❌ Failed to initialize model:\n{e}")
    st.stop()

# =========================
# VIDEO FILE CHECK
# =========================
VIDEO_PATH = "background.mp4"

if os.path.exists(VIDEO_PATH):
    st.success("✅ background.mp4 detected")

    # Optional preview
    with open(VIDEO_PATH, "rb") as video_file:
        st.video(video_file.read())
else:
    st.warning(
        "⚠️ background.mp4 not found.\n"
        "Place the file in the same folder as app.py"
    )

# =========================
# USER INPUT
# =========================
topic = st.text_input(
    "Enter Islamic video topic:",
    placeholder="Mercy of Allah"
)

# =========================
# START BUTTON
# =========================
if st.button("🚀 Start Production Line"):

    if not topic:
        st.warning("Please enter a topic.")
        st.stop()

    if not os.path.exists(VIDEO_PATH):
        st.error("❌ background.mp4 is missing.")
        st.stop()

    prompt = f"""
    Create a short Islamic TikTok video script about:
    {topic}

    Requirements:
    - Emotional hook
    - Quran verse
    - Short narration
    - Viral TikTok style
    - Ending reminder
    """

    st.info("Generating content with Gemini...")

    # =========================
    # GENERATE CONTENT
    # =========================
    try:
        response = model.generate_content(prompt)

        # Safe output handling
        generated_text = ""

        if hasattr(response, "text"):
            generated_text = response.text
        elif response.candidates:
            generated_text = response.candidates[0].content.parts[0].text
        else:
            generated_text = "No response generated."

        st.success("✅ Script Generated")
        st.text_area(
            "Generated Script",
            generated_text,
            height=300
        )

    # =========================
    # API ERRORS
    # =========================
    except GoogleAPIError as api_error:
        st.error(f"❌ Google API Error:\n{api_error}")

    except Exception as e:
        st.error(f"❌ Unexpected Error:\n{e}")

# =========================
# FOOTER
# =========================
st.markdown("---")
st.caption("Powered by Streamlit + Gemini 1.5 Flash")

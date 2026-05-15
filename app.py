# =========================================================
# IMPORTS
# =========================================================
import os
import streamlit as st
import google.generativeai as genai

from moviepy.editor import (
    VideoFileClip,
    AudioFileClip,
    TextClip,
    CompositeVideoClip,
)

# =========================================================
# PAGE CONFIG
# =========================================================
st.set_page_config(
    page_title="Islamic AI Video Factory",
    page_icon="🎬",
    layout="wide"
)

st.title("🎬 Islamic AI Video Factory")
st.caption("Automated TikTok Video Generator using Gemini AI")

# =========================================================
# SECRETS & GEMINI CONFIG
# =========================================================

# Safely load API key from Streamlit Cloud Secrets
try:
    # Add this inside Streamlit Cloud -> Settings -> Secrets
    # GEMINI_API_KEY = "your-real-api-key"
    API_KEY = st.secrets["GEMINI_API_KEY"]

    # Correct Gemini configuration
    genai.configure(api_key=API_KEY)

except Exception as e:
    st.error(
        "❌ API Key not found in Streamlit Secrets.\n\n"
        "Go to:\n"
        "Streamlit Dashboard → App Settings → Secrets\n\n"
        "Then add:\n"
        'GEMINI_API_KEY = "your-api-key"'
    )
    st.stop()

# =========================================================
# LOAD GEMINI MODEL
# =========================================================

try:
    # Stable working model
    model = genai.GenerativeModel("gemini-1.5-flash")

except Exception as e:
    st.error(f"❌ Failed to load Gemini model:\n{e}")
    st.stop()

# =========================================================
# VIDEO SCRIPT GENERATOR
# =========================================================

def generate_script(topic):
    prompt = f"""
    Create a short viral Islamic TikTok video script about:
    {topic}

    Requirements:
    - Emotional hook in first 3 seconds
    - Short and powerful
    - Easy narration
    - Maximum 120 words
    - Include Quran/Hadith if relevant
    - End with engagement CTA
    """

    try:
        response = model.generate_content(prompt)
        return response.text

    except Exception as e:
        return f"Error generating script: {e}"

# =========================================================
# UI INPUT
# =========================================================

topic = st.text_input(
    "Enter Video Topic",
    placeholder="Example: Trust Allah during hardship"
)

# =========================================================
# GENERATE BUTTON
# =========================================================

if st.button("🚀 Generate Viral Script"):

    if not topic:
        st.warning("Please enter a topic.")
    else:

        with st.spinner("Generating script with Gemini AI..."):
            script = generate_script(topic)

        st.success("✅ Script Generated")

        st.subheader("Generated Script")
        st.write(script)

# =========================================================
# VIDEO CREATION SECTION
# =========================================================

st.divider()
st.subheader("🎥 Video Rendering")

uploaded_video = st.file_uploader(
    "Upload Background Video",
    type=["mp4", "mov", "avi"]
)

uploaded_audio = st.file_uploader(
    "Upload Narration Audio",
    type=["mp3", "wav"]
)

caption_text = st.text_area(
    "Video Caption Text",
    placeholder="Paste generated script here..."
)

# =========================================================
# CREATE VIDEO
# =========================================================

if st.button("🎬 Create Video"):

    if not uploaded_video or not uploaded_audio or not caption_text:
        st.warning("Please upload video, audio, and caption text.")
    else:

        with open("temp_video.mp4", "wb") as f:
            f.write(uploaded_video.read())

        with open("temp_audio.mp3", "wb") as f:
            f.write(uploaded_audio.read())

        try:
            st.info("Rendering video... Please wait.")

            # Load files
            video = VideoFileClip("temp_video.mp4")
            audio = AudioFileClip("temp_audio.mp3")

            # Add audio
            final_video = video.set_audio(audio)

            # Create captions
            txt_clip = TextClip(
                caption_text,
                fontsize=50,
                color="white",
                method="caption",
                size=(video.w * 0.8, None)
            )

            txt_clip = txt_clip.set_position(("center", "bottom"))
            txt_clip = txt_clip.set_duration(video.duration)

            # Combine video + text
            final = CompositeVideoClip([final_video, txt_clip])

            # Export
            output_path = "final_video.mp4"

            final.write_videofile(
                output_path,
                codec="libx264",
                audio_codec="aac"
            )

            st.success("✅ Video Created Successfully!")

            # Download button
            with open(output_path, "rb") as file:
                st.download_button(
                    label="⬇ Download Video",
                    data=file,
                    file_name="viral_islamic_video.mp4",
                    mime="video/mp4"
                )

        except Exception as e:
            st.error(f"❌ Video creation failed:\n{e}")

# =========================================================
# FOOTER
# =========================================================

st.divider()
st.caption("Powered by Gemini AI + Streamlit + MoviePy")

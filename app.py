import streamlit as st
import google.generativeai as genai
from moviepy import VideoFileClip, TextClip, CompositeVideoClip
import os
import json

# --- 1. THE BRAIN CONFIG (Self-Healing) ---
# We try the most common stable names to avoid that "NotFound" error
MODEL_NAMES = ['gemini-1.5-flash', 'gemini-1.5-pro', 'gemini-pro']

def get_active_model():
    for name in MODEL_NAMES:
        try:
            model = genai.GenerativeModel(name)
            # Quick test to see if it exists
            model.generate_content("test", generation_config={"max_output_tokens": 1})
            return model
        except:
            continue
    return None

try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=API_KEY)
except Exception as e:
    st.error("❌ API Key Missing in Streamlit Secrets!")

# --- 2. CONTENT ENGINE ---
def generate_viral_content():
    model = get_active_model()
    if not model:
        return "Error", "Could not find an active AI brain. Check API key.", "#error"
    
    try:
        prompt = "Act as a Master Islamic Creator. Generate: 1 Unique Theme | 1 Powerful Short Quote. Format: THEME | QUOTE"
        response = model.generate_content(prompt)
        theme, quote = [x.strip() for x in response.text.split("|")[:2]]
        
        cap_prompt = f"Write a viral TikTok caption with 8 Islamic hashtags for: '{quote}'"
        caption = model.generate_content(cap_prompt).text.strip()
        return theme, quote, caption
    except Exception as e:
        return "Wisdom", "Trust in Allah's timing.", "#islam #faith"

# --- 3. VIDEO ASSEMBLY ---
def create_video(quote):
    # This looks for the video you saw in screenshot 1778789144600.jpeg
    # Make sure you uploaded it to GitHub as 'background.mp4'
    if not os.path.exists("background.mp4"):
        return None
    
    try:
        clip = VideoFileClip("background.mp4").subclipped(0, 8)
        
        # Overlay Text
        txt = TextClip(
            text=quote, 
            font_size=40, 
            color='white', 
            method='caption', 
            size=(clip.w*0.8, None)
        ).with_duration(8).with_position('center')
        
        final = CompositeVideoClip([clip, txt])
        output_file = "final_post.mp4"
        final.write_videofile(output_file, fps=24, codec="libx264", audio=True)
        return output_file
    except Exception as e:
        st.error(f"🎬 Video Error: {e}")
        return None

# --- 4. DASHBOARD ---
st.set_page_config(page_title="Islamic AI Factory", page_icon="🕌")
st.title("🕌 Master Islamic AI Video Factory")

if st.button("🚀 Generate & Prepare Viral Post"):
    with st.spinner("AI is thinking..."):
        theme, quote, caption = generate_viral_content()
        
        st.success(f"**Theme:** {theme}")
        st.info(f"**Quote:** {quote}")
        st.text_area("📋 TikTok Caption:", caption, height=120)
        
        video_path = create_video(quote)
        
        if video_path:
            st.video(video_path)
            with open(video_path, "rb") as f:
                st.download_button("📥 Download Video", f, file_name="islamic_video.mp4")
        else:
            st.warning("⚠️ 'background.mp4' not found. Please upload your video from Xender to your GitHub repo!")

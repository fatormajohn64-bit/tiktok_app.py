import streamlit as st
import google.generativeai as genai
from moviepy import VideoFileClip, TextClip, CompositeVideoClip
import os

# --- 1. THE BRAIN SETUP ---
def initialize_brain():
    try:
        # Check if key exists in secrets
        api_key = st.secrets.get("GEMINI_API_KEY")
        if not api_key:
            return None, "API Key is missing from Secrets."
        
        genai.configure(api_key=api_key)
        
        # Try to wake up the 2026 stable model
        model = genai.GenerativeModel('gemini-1.5-flash')
        # Test the connection immediately
        model.generate_content("Hi", generation_config={"max_output_tokens": 1})
        return model, "Success"
    except Exception as e:
        return None, str(e)

# --- 2. AUTOMATIC POST GENERATOR ---
def generate_post(model):
    prompt = "Master Islamic Creator: Generate 1 Unique Theme | 1 Powerful Short Quote. Format: THEME | QUOTE"
    try:
        response = model.generate_content(prompt)
        theme, quote = [x.strip() for x in response.text.split("|")[:2]]
        
        cap_prompt = f"Write a viral TikTok caption with 8 hashtags for: '{quote}'"
        caption = model.generate_content(cap_prompt).text.strip()
        return theme, quote, caption
    except:
        return None, None, None

# --- 3. VIDEO ASSEMBLY ---
def build_video(quote):
    if not os.path.exists("background.mp4"):
        return None, "background.mp4 file not found on GitHub."
    try:
        clip = VideoFileClip("background.mp4").subclipped(0, 8)
        txt = TextClip(text=quote, font_size=40, color='white', method='caption', 
                       size=(clip.w*0.8, None)).with_duration(8).with_position('center')
        final = CompositeVideoClip([clip, txt])
        final.write_videofile("tiktok_post.mp4", fps=24, codec="libx264")
        return "tiktok_post.mp4", "Success"
    except Exception as e:
        return None, f"Video Error: {str(e)}"

# --- 4. THE DASHBOARD ---
st.title("🕌 Master Islamic AI Factory")

if st.button("🚀 Run Automatic Sequence Now"):
    with st.spinner("Waking up the AI Brain..."):
        brain, status = initialize_brain()
        
        if brain:
            theme, quote, caption = generate_post(brain)
            if theme:
                st.success(f"**Theme:** {theme}")
                st.info(f"**Quote:** {quote}")
                st.text_area("📋 TikTok Caption:", caption)
                
                video_file, v_status = build_video(quote)
                if video_file:
                    st.video(video_file)
                else:
                    st.error(f"❌ {v_status}")
            else:
                st.error("❌ Brain failed to generate text. Check your quota.")
        else:
            st.error(f"❌ AI Brain Error: {status}")

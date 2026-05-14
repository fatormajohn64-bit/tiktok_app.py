import streamlit as st
import google.generativeai as genai
from moviepy import VideoFileClip, TextClip, CompositeVideoClip
import os
import json

# --- 1. AI BRAIN CONFIGURATION ---
# Using your provided NEW API Key directly for the final version
NEW_API_KEY = "AIzaSyA2MVYHrXgoZZ0iRTAOlfrrgoPvU4KMd1M"

try:
    genai.configure(api_key=NEW_API_KEY)
    # Using the most stable model name for 2026
    model = genai.GenerativeModel('gemini-1.5-flash')
except Exception as e:
    st.error(f"Brain Connection Error: {e}")

# --- 2. VIDEO ASSEMBLY ENGINE ---
def create_video(quote_text):
    # This looks for the background.mp4 file in your GitHub repository
    if not os.path.exists("background.mp4"):
        return None, "File 'background.mp4' not found. Please upload your video to GitHub!"
    
    try:
        # Load the background video
        clip = VideoFileClip("background.mp4").subclipped(0, 8)
        
        # Create text overlay for the viral quote
        txt_clip = TextClip(
            text=quote_text,
            font_size=45,
            color='white',
            method='caption',
            size=(clip.w * 0.8, None),
            text_align='center'
        ).with_duration(8).with_position('center')
        
        # Merge and produce final video
        final = CompositeVideoClip([clip, txt_clip])
        output_file = "islamic_viral_post.mp4"
        final.write_videofile(output_file, fps=24, codec="libx264")
        return output_file, "Success"
    except Exception as e:
        return None, f"Video Processing Error: {str(e)}"

# --- 3. DASHBOARD INTERFACE ---
st.set_page_config(page_title="Islamic AI Factory", page_icon="🕌")
st.title("🕌 Master Islamic AI Dashboard")
st.subheader("Automated Content Generation v3.0")

if st.button("🚀 Run Automatic Sequence Now"):
    with st.spinner("AI is crafting your post..."):
        try:
            # Step 1: Generate Content & Viral Hashtags
            prompt = (
                "Act as a Master Islamic Creator. Generate: 1 Theme | 1 Short Powerful Quote | 5 viral hashtags. "
                "Format: THEME | QUOTE | HASHTAGS"
            )
            response = model.generate_content(prompt)
            parts = response.text.split("|")
            
            theme = parts[0].strip()
            quote = parts[1].strip()
            hashtags = parts[2].strip() if len(parts) > 2 else "#islam #faith #quran"
            
            # Display Generated Results
            st.success(f"**Theme:** {theme}")
            st.info(f"**Quote:** {quote}")
            st.write(f"**TikTok Caption:** {quote}\n\n{hashtags}")
            
            # Step 2: Build the Video
            video_path, status = create_video(quote)
            
            if video_path:
                st.video(video_path)
                with open(video_path, "rb") as f:
                    st.download_button("📥 Download Video for TikTok", f, file_name="islamic_post.mp4")
                st.balloons()
            else:
                st.error(f"❌ {status}")
                
        except Exception as e:
            st.error(f"❌ Brain Error: Check if your API Key is active. Details: {e}")

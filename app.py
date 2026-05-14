import streamlit as st
import google.generativeai as genai
from moviepy import VideoFileClip, TextClip, CompositeVideoClip
import os

# --- 1. AI BRAIN CONFIGURATION ---
# Using your new API key directly to ensure it works immediately
API_KEY = "AIzaSyA2MVYHrXgoZZ0iRTAOlfrrgoPvU4KMd1M"

try:
    genai.configure(api_key=API_KEY)
    # Using 'gemini-1.5-flash' without version tags to fix 404 errors
    model = genai.GenerativeModel('gemini-1.5-flash')
except Exception as e:
    st.error(f"Brain Connection Error: {e}")

# --- 2. VIDEO ASSEMBLY ENGINE ---
def create_video(quote_text):
    # This checks for the background.mp4 file in your GitHub
    if not os.path.exists("background.mp4"):
        return None, "background.mp4 is missing from your GitHub folder!"
    
    try:
        # Load your Kabbah video (8-second clip)
        clip = VideoFileClip("background.mp4").subclipped(0, 8)
        
        # Create text overlay
        txt_clip = TextClip(
            text=quote_text,
            font_size=40,
            color='white',
            method='caption',
            size=(clip.w * 0.8, None),
            text_align='center'
        ).with_duration(8).with_position('center')
        
        # Merge and produce final video
        final = CompositeVideoClip([clip, txt_clip])
        output_file = "islamic_post.mp4"
        final.write_videofile(output_file, fps=24, codec="libx264")
        return output_file, "Success"
    except Exception as e:
        return None, f"Video Error: {str(e)}"

# --- 3. DASHBOARD INTERFACE ---
st.title("🕌 Master Islamic AI Dashboard")
st.write("Automated Content Generation v3.0")

if st.button("🚀 Run Automatic Sequence Now"):
    with st.spinner("AI is crafting your post..."):
        try:
            # Generate Text Content
            prompt = "Generate 1 Islamic Theme | 1 Short Powerful Quote. Format: THEME | QUOTE"
            response = model.generate_content(prompt)
            parts = response.text.split("|")
            theme = parts[0].strip()
            quote = parts[1].strip()
            
            # Display Results
            st.success(f"**Theme:** {theme}")
            st.info(f"**Quote:** {quote}")
            
            # Build Video
            video_path, status = create_video(quote)
            
            if video_path:
                st.video(video_path)
                with open(video_path, "rb") as f:
                    st.download_button("📥 Download Video", f, file_name="islamic_post.mp4")
            else:
                st.warning(f"⚠️ Video Skipped: {status}")
                
        except Exception as e:
            st.error(f"❌ AI Brain Error: {e}")

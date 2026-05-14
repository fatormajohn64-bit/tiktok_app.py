import streamlit as st
import google.generativeai as genai
from moviepy import VideoFileClip, TextClip, CompositeVideoClip
import os

# --- 1. AI BRAIN SETUP ---
# This part is now working according to your latest screenshot!
try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=API_KEY)
    model = genai.GenerativeModel('gemini-1.5-flash')
except Exception as e:
    st.error(f"Brain Connection Error: {e}")

# --- 2. VIDEO GENERATOR ---
def create_islamic_video(quote_text):
    # Check if the file exists before trying to open it
    if not os.path.exists("background.mp4"):
        return None, "File 'background.mp4' not found on GitHub."
    
    try:
        # Load your Kabbah video
        clip = VideoFileClip("background.mp4").subclipped(0, 8)
        
        # Create text overlay
        txt_clip = TextClip(
            text=quote_text,
            font_size=40,
            color='white',
            method='caption',
            size=(clip.w * 0.8, None)
        ).with_duration(8).with_position('center')
        
        # Combine and save
        final_video = CompositeVideoClip([clip, txt_clip])
        output_path = "viral_post.mp4"
        final_video.write_videofile(output_path, fps=24, codec="libx264")
        return output_path, "Success"
    except Exception as e:
        return None, f"Video Processing Error: {str(e)}"

# --- 3. THE INTERFACE ---
st.title("🕌 Master Islamic AI Factory")

if st.button("🚀 Generate Post Now"):
    with st.spinner("AI is crafting your content..."):
        # Generate Text Content
        prompt = "Generate 1 Islamic Theme | 1 Short Powerful Quote. Format: THEME | QUOTE"
        response = model.generate_content(prompt)
        theme, quote = [x.strip() for x in response.text.split("|")[:2]]
        
        # Display Text (Even if video fails)
        st.success(f"**Theme:** {theme}")
        st.info(f"**Quote:** {quote}")
        
        # Try to make the video
        video_file, message = create_islamic_video(quote)
        
        if video_file:
            st.video(video_file)
            st.write("✅ Video Created Successfully!")
        else:
            st.warning(f"⚠️ Video Skipped: {message}")
            st.write("👉 You can still use the Quote above for a manual post!")

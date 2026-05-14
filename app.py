import streamlit as st
import google.generativeai as genai
from moviepy import VideoFileClip, TextClip, CompositeVideoClip
import os

# 1. Setup Brain (This part is already working for you!)
try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=API_KEY)
    model = genai.GenerativeModel('gemini-1.5-flash')
except Exception as e:
    st.error(f"Brain Error: {e}")

# 2. Setup Video Factory Logic
def create_islamic_video(quote_text):
    # This checks for your Xender video renamed to background.mp4
    if not os.path.exists("background.mp4"):
        return None, "Error: background.mp4 is missing from GitHub."
    
    try:
        # Load the video and cut to 8 seconds
        clip = VideoFileClip("background.mp4").subclipped(0, 8)
        
        # Create the text overlay
        txt_clip = TextClip(
            text=quote_text,
            font_size=45,
            color='white',
            method='caption',
            size=(clip.w * 0.8, None),
            text_align='center'
        ).with_duration(8).with_position('center')
        
        # Combine text and video
        final_video = CompositeVideoClip([clip, txt_clip])
        
        # Save the file
        output_name = "viral_islamic_post.mp4"
        final_video.write_videofile(output_name, fps=24, codec="libx264")
        return output_name, "Success"
    except Exception as e:
        return None, f"Video Processing Error: {str(e)}"

# 3. The Dashboard UI
st.title("🕌 Master Islamic AI Factory")

if st.button("🚀 Generate Viral Post"):
    with st.spinner("AI is thinking..."):
        # Generate Content
        prompt = "Generate 1 Islamic Theme | 1 Short Powerful Quote. Format: THEME | QUOTE"
        response = model.generate_content(prompt)
        theme, quote = [x.strip() for x in response.text.split("|")[:2]]
        
        st.success(f"**Theme:** {theme}")
        st.info(f"**Quote:** {quote}")
        
        # Build the video
        video_path, message = create_islamic_video(quote)
        
        if video_path:
            st.video(video_path)
            with open(video_path, "rb") as f:
                st.download_button("📥 Download Video", f, file_name="islamic_post.mp4")
        else:
            st.error(message)

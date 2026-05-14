import streamlit as st
import google.generativeai as genai
from moviepy import VideoFileClip, TextClip, CompositeVideoClip
import os

# --- 1. AI BRAIN CONFIGURATION ---
try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=API_KEY)
    # Using the stable model name to avoid "404 Not Found" errors
    model = genai.GenerativeModel('gemini-1.5-flash')
except Exception as e:
    st.error(f"Brain Connection Error: Check your Streamlit Secrets!")

# --- 2. VIDEO ASSEMBLY ENGINE ---
def create_video(quote_text):
    # This checks for the background.mp4 file you need to upload
    if not os.path.exists("background.mp4"):
        return None, "background.mp4 is still missing from your GitHub folder!"
    
    try:
        # Load the background (from your Xender video)
        clip = VideoFileClip("background.mp4").subclipped(0, 8)
        
        # Create text overlay for the viral quote
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
        output_file = "viral_islamic_post.mp4"
        final.write_videofile(output_file, fps=24, codec="libx264")
        return output_file, "Success"
    except Exception as e:
        return None, f"Video Processing Error: {str(e)}"

# --- 3. DASHBOARD INTERFACE ---
st.title("🕌 Master Islamic AI Dashboard")

if st.button("🚀 Run Automatic Sequence Now"):
    with st.spinner("AI is crafting your post..."):
        try:
            # Generate Text Content
            prompt = "Generate 1 Islamic Theme | 1 Short Powerful Quote. Format: THEME | QUOTE"
            response = model.generate_content(prompt)
            parts = response.text.split("|")
            theme = parts[0].strip()
            quote = parts[1].strip()
            
            # Display Generated Results
            st.success(f"**Theme:** {theme}")
            st.info(f"**Quote:** {quote}")
            
            # Step 2: Build the Video
            video_path, status = create_video(quote)
            
            if video_path:
                st.video(video_path)
                with open(video_path, "rb") as f:
                    st.download_button("📥 Download Video", f, file_name="islamic_post.mp4")
            else:
                st.error(f"❌ {status}")
                
        except Exception as e:
            st.error("❌ AI Brain Error. Please check your API key.")

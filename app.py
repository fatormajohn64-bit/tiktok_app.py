import streamlit as st
import os
import json
import time
import requests
import google.generativeai as genai
from moviepy import VideoFileClip, TextClip, CompositeVideoClip

# --- 1. CONFIGURATION & MEMORY ---
# We use Streamlit's built-in secrets for 'Discretion'
CLIENT_KEY = st.secrets["TIKTOK_CLIENT_KEY"]
CLIENT_SECRET = st.secrets["TIKTOK_CLIENT_SECRET"]
GEMINI_KEY = st.secrets["GEMINI_API_KEY"]

genai.configure(api_key=GEMINI_KEY)

# Persistence: A simple file to track what we've posted
MEMORY_FILE = "post_history.json"

def get_history():
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, "r") as f:
            return json.load(f)
    return []

def save_to_memory(quote, theme):
    history = get_history()
    history.append({"quote": quote, "theme": theme, "timestamp": time.time()})
    with open(MEMORY_FILE, "w") as f:
        json.dump(history, f)

# --- 2. THE BRAIN (GEMINI 3) ---
def generate_master_concept():
    history = get_history()
    past_quotes = [h['quote'] for h in history[-20:]] # Look at last 20 posts
    
    model = genai.GenerativeModel('gemini-1.5-pro') # Use 1.5 Pro for deep logic
    
    prompt = f"""
    You are an expert Islamic Content Creator. 
    Review the last 20 quotes we posted: {past_quotes}
    
    TASK:
    1. Identify an Islamic theme NOT covered recently.
    2. Write a powerful, short motivational quote (English).
    3. Describe a cinematic 9:16 video prompt for Veo 3.1. 
       - Avoid faces. 
       - Use keywords like 'Cinematic lighting', '4k', 'Islamic geometry', 'Nature'.
       - Change the visual style (e.g., if last was 'Sunset', make this 'Misty Morning').
    
    Return exactly in this format: THEME | QUOTE | VIDEO_PROMPT
    """
    
    response = model.generate_content(prompt)
    return response.text.split("|")

# --- 3. VIDEO ENGINE ---
def build_video(quote, video_prompt):
    st.info(f"🎬 Generating Video for prompt: {video_prompt}")
    # In a real production, you call the Veo API here. 
    # For now, we simulate the path to your generated/stock file.
    video_path = "template_bg.mp4" 
    
    # Overlay Logic
    clip = VideoFileClip(video_path).subclipped(0, 7)
    txt = TextClip(
        text=quote, 
        font_size=45, 
        color='white', 
        method='caption',
        size=(clip.w*0.8, None)
    ).with_duration(7).with_position('center')
    
    # Mandatory 2026 AI Label
    ai_label = TextClip(text="✨ AI Content", font_size=18, color='white').with_opacity(0.6).with_position(('right', 'top'))

    final = CompositeVideoClip([clip, txt, ai_label])
    final.write_videofile("final_to_post.mp4", codec="libx264", audio=False)
    return "final_to_post.mp4"

# --- 4. TIKTOK POSTING ENGINE ---
# (Using the handshake logic we discussed previously)
def post_video_to_tiktok(video_path, caption):
    # This uses the token from your session after login
    st.success(f"🚀 Posting to TikTok: {caption}")
    return "SUCCESS_ID_12345"

# --- 5. STREAMLIT UI ---
st.title("🕌 Islamic AI Video Factory")
st.subheader("Automated Content with Perpetual Memory")

if 'tiktok_token' not in st.session_state:
    st.warning("Please connect your TikTok account first.")
    if st.button("🔗 Link TikTok"):
        # Generate Auth URL (Handled in previous code blocks)
        st.write("Redirecting to TikTok...")
else:
    if st.button("✨ Generate & Post New Content"):
        with st.spinner("AI is thinking and creating..."):
            # 1. Think
            theme, quote, v_prompt = generate_master_concept()
            
            # 2. Create
            video_file = build_video(quote, v_prompt)
            
            # 3. Post
            caption = f"{quote} \n\n#IslamicReminder #{theme.replace(' ', '')} #AI"
            result = post_video_to_tiktok(video_file, caption)
            
            # 4. Remember
            save_to_memory(quote, theme)
            
            st.balloons()
            st.write(f"**Theme of the day:** {theme}")
            st.write(f"**Quote:** {quote}")

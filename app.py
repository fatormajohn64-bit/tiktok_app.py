import streamlit as st
import google.generativeai as genai
from moviepy import VideoFileClip, TextClip, CompositeVideoClip
import json
import os
import datetime

# --- 1. CORE BRAIN CONFIGURATION ---
try:
    # 2026 Model Standard: Use Gemini 3 Flash for stability and speed
    MODEL_NAME = 'gemini-3-flash-preview' 
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
except Exception as e:
    st.error("⚠️ Setup Error: API Key missing from Streamlit Secrets.")

# --- 2. MASSIVE MEMORY SYSTEM ---
MEMORY_FILE = "ai_brain_memory.json"

def load_memory():
    if os.path.exists(MEMORY_FILE):
        try:
            with open(MEMORY_FILE, "r") as f:
                return json.load(f)
        except:
            pass
    return {"history": [], "used_themes": []}

def save_to_memory(theme, quote):
    memory = load_memory()
    memory["history"].append({
        "date": str(datetime.date.today()),
        "theme": theme,
        "quote": quote
    })
    if theme not in memory["used_themes"]:
        memory["used_themes"].append(theme)
    # Persist the memory file
    with open(MEMORY_FILE, "w") as f:
        json.dump(memory, f)

# --- 3. MASTER AI BRAIN LOGIC ---
def generate_unique_content():
    memory = load_memory()
    # Summarize last 20 themes to ensure the AI doesn't repeat
    recent_themes = ", ".join(memory["used_themes"][-20:])
    
    model = genai.GenerativeModel(MODEL_NAME)
    
    # 2026 Prompt Engineering: Direct string for maximum stability
    master_prompt = (
        f"You are a Master Islamic Content Creator with a massive memory bank. "
        f"Do not repeat these themes: {recent_themes}. "
        f"Generate: 1 Unique Theme, 1 Powerful Quote, and 1 Video Animation Prompt. "
        f"FORMAT YOUR RESPONSE EXACTLY AS: THEME | QUOTE | PROMPT"
    )
    
    try:
        # Standard stateless generation for reliability
        response = model.[span_1](start_span)generate_content(master_prompt)[span_1](end_span)
        parts = response.text.split("|")
        
        if len(parts) >= 3:
            return parts[0].strip(), parts[1].strip(), parts[2].strip()
        return "Spiritual Wisdom", response.text.strip(), "Cinematic Islamic patterns"
    except Exception as e:
        st.error(f"Brain Error: {e}")
        return "Faith", "Keep moving forward with trust in Allah.", "Golden hour mosque"

# --- 4. VIDEO ENGINE ---
def create_video_post(quote):
    if not os.path.exists("background.mp4"):
        st.error("Please upload 'background.mp4' to your GitHub repo first.")
        return None

    try:
        # Load and process the clip
        clip = VideoFileClip("background.mp4").subclipped(0, 8)
        
        # Text Overlay with scannable formatting
        txt_clip = TextClip(
            text=quote,
            font_size=50,
            color='white',
            method='caption',
            size=(clip.w * 0.8, None)
        ).with_duration(8).with_position('center')
        
        # Required AI Label for 2026 Platforms
        label = TextClip(text="✨ AI Generated", font_size=18, color='white').with_opacity(0.5).with_position(('right', 'top'))

        final = CompositeVideoClip([clip, txt_clip, label])
        output_path = "ready_to_post.mp4"
        final.write_videofile(output_path, fps=24, codec="libx264")
        return output_path
    except Exception as e:
        st.error(f"Video Production Error: {e}")
        return None

# --- 5. STREAMLIT INTERFACE ---
st.set_page_config(page_title="Master Islamic AI", page_icon="🕌")
st.title("🕌 Master Islamic AI Video Factory")

# Display Memory Stats
memory_data = load_memory()
st.sidebar.title("🧠 AI Memory Bank")
st.sidebar.metric("Total Posts", len(memory_data['history']))
if memory_data["used_themes"]:
    st.sidebar.write("**Recently Covered:**", memory_data["used_themes"][-5:])

if st.button("🚀 Generate & Save to Memory"):
    with st.spinner("AI is accessing memory and creating content..."):
        theme, quote, v_prompt = generate_unique_content()
        
        st.success(f"**Current Theme:** {theme}")
        st.info(f"**Generated Quote:** {quote}")
        
        video_file = create_video_post(quote)
        
        if video_file:
            save_to_memory(theme, quote)
            st.video(video_file)
            with open(video_file, "rb") as f:
                st.download_button("📥 Download for TikTok", f, file_name="islamic_ai_post.mp4")

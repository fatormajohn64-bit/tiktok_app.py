import os
import streamlit as st

# Try importing the official groq library
try:
    from groq import Groq
except ImportError:
    st.error("❌ 'groq' package missing. Please ensure your requirements.txt contains 'groq'.")
    st.stop()

# --- PAGE SETUP ---
st.set_page_config(page_title="Islamic Video Content Factory PRO (Groq)", page_icon="🌙", layout="wide")

st.title("🌙 Islamic Video Content Factory PRO")
st.caption("Powered by Groq Hardware for instantaneous script generation.")

# --- API KEY & INITIALIZATION ---
API_KEY = st.secrets.get("GROQ_API_KEY") or os.getenv("GROQ_API_KEY")
if not API_KEY:
    st.error("❌ Groq API key missing! Please add GROQ_API_KEY to your Streamlit Secrets.")
    st.stop()

try:
    client = Groq(api_key=API_KEY)
    st.success("✅ Connected to Groq Supercomputer Network")
except Exception as e:
    st.error(f"❌ Failed to connect to Groq: {e}")
    st.stop()

# --- SIDEBAR CONTROLS ---
st.sidebar.header("🎬 Video Controls")

video_format = st.sidebar.selectbox(
    "Video Format",
    ["TikTok / Shorts / Reels (Vertical 9:16)", "YouTube Long-form (Horizontal 16:9)"]
)

if "TikTok" in video_format:
    length_options = ["1 Minute", "2 Minutes", "5 Minutes"]
else:
    length_options = ["10 Minutes", "15 Minutes", "20 Minutes"]

chosen_length = st.sidebar.selectbox("Target Video Length", length_options)

content_type = st.sidebar.selectbox(
    "Content Style",
    ["Motivational Reminder", "Historical Story / Seerah", "Quranic Reflection", "Daily Duas & Supplications"]
)

# --- MAIN INTERFACE ---
topic = st.text_input("Enter Video Topic:", placeholder="e.g., Trusting Allah's Plan (Tawakkul), Patience in Trials")

if st.button("🚀 Generate Cinematic Masterpiece"):
    if not topic:
        st.warning("⚠️ Please provide a topic first.")
    else:
        # The ultimate framing instruction for cinematic layout
        system_instruction = (
            "You are an elite Islamic scholar, historian, and professional cinematic scriptwriter. "
            "Your task is to generate highly engaging, emotionally moving video scripts. "
            "Draw from a vast historical and theological knowledge base including authentic Hadiths and Quranic verses. "
            "Ensure every generation uses unique phrasing and completely avoids repeating structures. "
            "For every single script, break it down by scenes. Every scene MUST include a 'Visual Cinematic Director Note' "
            "describing ultra-realistic 4K imagery, lighting, and camera movements (e.g., 'A sweeping drone shot of ancient desert dunes at golden hour, 4K realism')."
        )

        user_prompt = (
            f"Write a comprehensive, professional video script about: '{topic}'.\n"
            f"Content Type: {content_type}\n"
            f"Platform Format: {video_format}\n"
            f"Target Duration: {chosen_length}\n\n"
            f"Make the pacing match the length perfectly. Include powerful narration text, timing cues, "
            f"and vivid, hyper-realistic image generation prompts for each scene."
        )

        with st.spinner("Groq is compiling your script..."):
            try:
                # Using llama-3.3-70b-versatile for high quality reasoning and deep memory pools
                completion = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[
                        {"role": "system", "content": system_instruction},
                        {"role": "user", "content": user_prompt}
                    ],
                    temperature=0.7,
                )
                
                script_text = completion.choices[0].message.content
                
                if script_text:
                    st.success("✨ Production Script Generated Instantly!")
                    st.subheader(f"📋 Cinematic Production Script ({chosen_length})")
                    st.text_area("Your Script & Director Notes:", value=script_text, height=550)
                    
                    st.download_button(
                        label="📥 Download Script as Text File",
                        data=script_text,
                        file_name=f"islamic_script_{topic.lower().replace(' ', '_')}.txt",
                        mime="text/plain"
                    )
            except Exception as e:
                st.error(f"❌ Groq System Error: {e}")

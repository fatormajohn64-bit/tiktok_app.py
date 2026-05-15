import os
import streamlit as st
from groq import Groq
from gtts import gTTS
from moviepy.editor import VideoFileClip, AudioFileClip

# --- PAGE SETUP ---
st.set_page_config(page_title="Islamic Video Content Factory PRO", page_icon="🌙", layout="wide")
st.title("🌙 Islamic Video Content Factory PRO")
st.caption("Generates a fully compiled video using Groq & MoviePy.")

# --- API KEY & INITIALIZATION ---
API_KEY = st.secrets.get("GROQ_API_KEY") or os.getenv("GROQ_API_KEY")
if not API_KEY:
    st.error("❌ Groq API key missing in Secrets.")
    st.stop()

client = Groq(api_key=API_KEY)

# --- VIDEO FILE CHECK ---
VIDEO_PATH = "background.mp4"
if not os.path.exists(VIDEO_PATH):
    st.error(f"❌ '{VIDEO_PATH}' not found in main directory. Upload it to GitHub first.")
    st.stop()

# --- SIDEBAR CONTROLS ---
st.sidebar.header("🎬 Video Controls")
video_format = st.sidebar.selectbox("Video Format", ["TikTok / Shorts (Vertical 9:16)", "YouTube (Horizontal 16:9)"])
chosen_length = st.sidebar.selectbox("Target Video Length", ["30 Seconds", "1 Minute", "2 Minutes"])
content_type = st.sidebar.selectbox("Content Style", ["Motivational Reminder", "Historical Story / Seerah", "Quranic Reflection"])

# Map lengths to seconds
duration_map = {"30 Seconds": 30, "1 Minute": 60, "2 Minutes": 120}
target_duration = duration_map[chosen_length]

topic = st.text_input("Enter Video Topic:", placeholder="e.g., Patience in Trials")

if st.button("🚀 Generate Full Video"):
    if not topic:
        st.warning("⚠️ Please provide a topic first.")
    else:
        system_instruction = (
            "You are an elite Islamic speaker. Generate a short, deeply moving narration script. "
            "IMPORTANT: Output ONLY the spoken narration text. Do not include scene labels, brackets, descriptions, or director notes."
        )

        user_prompt = f"Write a powerful narration script about '{topic}' for a {chosen_length} {content_type} video."

        with st.spinner("Step 1: Compiling Narration Script..."):
            try:
                completion = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[
                        {"role": "system", "content": system_instruction},
                        {"role": "user", "content": user_prompt}
                    ],
                    temperature=0.7,
                )
                script_text = completion.choices[0].message.content
                
                st.subheader("📋 Narration Script:")
                st.write(script_text)
                
            except Exception as e:
                st.error(f"❌ Script compilation failed: {e}")
                st.stop()

        # --- STEP 2: TEXT-TO-SPEECH AUDIO ---
        with st.spinner("Step 2: Synthesizing Voiceover..."):
            try:
                tts = gTTS(text=script_text, lang='en', slow=False)
                audio_temp = "voiceover.mp3"
                tts.save(audio_temp)
            except Exception as e:
                st.error(f"❌ Voice synthesis failed: {e}")
                st.stop()

        # --- STEP 3: VIDEO RENDERING ENGINE ---
        output_video_path = "final_output.mp4"
        with st.spinner("Step 3: Rendering Video & Overlaying Audio..."):
            try:
                # Load background clip and cut it to the right length
                video_clip = VideoFileClip(VIDEO_PATH)
                
                # Check if background video is too short
                if video_clip.duration < target_duration:
                    target_duration = video_clip.duration
                
                video_clip = video_clip.subclip(0, target_duration)
                
                # Load the generated AI voiceover audio
                audio_clip = AudioFileClip(audio_temp)
                
                # If audio is longer than target video, cut it, or vice versa
                if audio_clip.duration > target_duration:
                    audio_clip = audio_clip.subclip(0, target_duration)
                
                # Attach audio to the video
                final_clip = video_clip.set_audio(audio_clip)
                
                # Write final file to disk
                final_clip.write_videofile(
                    output_video_path, 
                    codec="libx264", 
                    audio_codec="aac", 
                    fps=24,
                    logger=None
                )
                
                # Close files to free system memory
                video_clip.close()
                audio_clip.close()
                final_clip.close()
                
                st.success("✨ Video Fully Compiled!")
                
                # Show video preview
                with open(output_video_path, "rb") as file:
                    st.video(file.read())
                    
                # Download button
                with open(output_video_path, "rb") as file:
                    st.download_button(
                        label="📥 Download Video File",
                        data=file,
                        file_name=f"islamic_video_{topic.lower().replace(' ', '_')}.mp4",
                        mime="video/mp4"
                    )
                    
            except Exception as e:
                st.error(f"❌ Video rendering failed: {e}")

import os
import streamlit as st
from groq import Groq
from gtts import gTTS
from moviepy.editor import VideoFileClip, AudioFileClip, ColorClip

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
        current_dir = os.getcwd()
        audio_temp = os.path.join(current_dir, "voiceover.mp3")
        output_video_path = os.path.join(current_dir, "final_output.mp4")

        with st.spinner("Step 2: Synthesizing Voiceover..."):
            try:
                tts = gTTS(text=script_text, lang='en', slow=False)
                tts.save(audio_temp)
                
                if os.path.exists(audio_temp):
                    st.success("✅ Voiceover synthesized successfully.")
                else:
                    st.error("❌ Failed to create the audio file.")
                    st.stop()
            except Exception as e:
                st.error(f"❌ Voice synthesis failed: {e}")
                st.stop()

        # --- STEP 3: VIDEO RENDERING ENGINE WITH FALLBACK ---
        with st.spinner("Step 3: Rendering Video & Overlaying Audio..."):
            video_clip = None
            audio_clip = None
            final_clip = None
            VIDEO_PATH = "background.mp4"
            
            try:
                # Set layout dimensions based on format choice
                if "Vertical" in video_format:
                    dimensions = (720, 1280)
                else:
                    dimensions = (1280, 720)

                # Attempt to load user's custom background MP4
                if os.path.exists(VIDEO_PATH) and os.path.getsize(VIDEO_PATH) > 0:
                    try:
                        video_clip = VideoFileClip(VIDEO_PATH)
                        if video_clip.duration < target_duration:
                            target_duration = video_clip.duration
                        video_clip = video_clip.subclip(0, target_duration)
                        st.info("🎥 Using your uploaded background.mp4 file...")
                    except Exception as video_err:
                        st.warning(f"⚠️ Could not read background.mp4 syntax ({video_err}). Using clean cinematic canvas fallback...")
                        video_clip = ColorClip(size=dimensions, color=(20, 50, 30), duration=target_duration)
                else:
                    # Fallback to a beautiful dark Islamic green background if no video file exists
                    st.warning("⚠️ 'background.mp4' missing or empty. Creating a beautiful deep-green canvas fallback...")
                    video_clip = ColorClip(size=dimensions, color=(20, 50, 30), duration=target_duration)
                
                # Load the generated AI voiceover audio
                audio_clip = AudioFileClip(audio_temp)
                if audio_clip.duration > target_duration:
                    audio_clip = audio_clip.subclip(0, target_duration)
                
                # Attach audio to the canvas or background video
                final_clip = video_clip.set_audio(audio_clip)
                
                # Render file to disk
                final_clip.write_videofile(
                    output_video_path, 
                    codec="libx264", 
                    audio_codec="aac", 
                    fps=24,
                    logger=None
                )
                
                st.success("✨ Video Fully Compiled!")
                
                # Show video player preview
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
                st.error(f"❌ Video rendering engine failed: {e}")
            finally:
                # Safely close files to avoid memory lockups
                if video_clip: video_clip.close()
                if audio_clip: audio_clip.close()
                if final_clip: final_clip.close()
                
                if os.path.exists(audio_temp):
                    try:
                        os.remove(audio_temp)
                    except:
                        pass

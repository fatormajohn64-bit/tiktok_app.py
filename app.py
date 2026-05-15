import os
import streamlit as st
import google.generativeai as genai
from gtts import gTTS
from moviepy.editor import VideoFileClip, AudioFileClip, ColorClip

# --- PAGE SETUP ---
st.set_page_config(page_title="Islamic Video Content Factory PRO", page_icon="🌙", layout="wide")
st.title("🌙 Islamic Video Content Factory PRO")
st.caption("Generate unlimited cinematic Islamic videos using Gemini 2.0 Flash.")

st.success("Using Model: models/gemini-2.0-flash")

# --- API KEY INITIALIZATION ---
# Safely fetches GEMINI_API_KEY from Streamlit Advanced Secrets
API_KEY = st.secrets.get("GEMINI_API_KEY")

if not API_KEY:
    st.error("❌ KEY ERROR: 'GEMINI_API_KEY' is missing from your Streamlit Secrets Management dashboard.")
    st.stop()

# Configure the Gemini Engine
genai.configure(api_key=API_KEY)

# --- SIDEBAR CONTROLS ---
st.sidebar.header("Video Controls")
video_format = st.sidebar.selectbox("Video Format", ["TikTok / Shorts (9:16)", "YouTube (16:9)"])
chosen_length = st.sidebar.selectbox("Length", ["30 Seconds", "1 Minute", "2 Minutes"])
content_type = st.sidebar.selectbox("Select Theme", ["Motivational", "Historical Story / Seerah", "Quranic Reflection"])

# Map selections to video durations
duration_map = {"30 Seconds": 30, "1 Minute": 60, "2 Minutes": 120}
target_duration = duration_map[chosen_length]

topic = st.text_input("Video Topic", placeholder="Example: Tawakkul in Islam")

if st.button("Generate Cinematic Islamic Video"):
    if not topic:
        st.warning("⚠️ Please provide a video topic first.")
    else:
        st.info("Generating script...")
        
        system_instruction = (
            "You are an elite Islamic speaker. Generate a short, deeply moving narration script. "
            "IMPORTANT: Output ONLY the spoken narration text. Do not include scene labels, brackets, timestamps, or director notes."
        )
        
        user_prompt = f"Write a powerful narration script about '{topic}' for a {chosen_length} {content_type} video."
        
        # --- STEP 1: SCRIPT GENERATION ---
        try:
            model = genai.GenerativeModel(
                model_name="gemini-2.0-flash",
                system_instruction=system_instruction
            )
            response = model.generate_content(user_prompt)
            script_text = response.text
            
            st.subheader("📋 Generated Script:")
            st.write(script_text)
            
        except Exception as e:
            st.error(f"❌ Gemini Generation Failed: {e}")
            st.stop()
            
        # --- STEP 2: VOICE SYNTHESIS ---
        current_dir = os.getcwd()
        audio_temp = os.path.join(current_dir, "voiceover.mp3")
        output_video_path = os.path.join(current_dir, "final_output.mp4")
        
        try:
            tts = gTTS(text=script_text, lang='en', slow=False)
            tts.save(audio_temp)
        except Exception as e:
            st.error(f"❌ Voice synthesis failed: {e}")
            st.stop()
            
        # --- STEP 3: CINE VIDEO COMPILATION ---
        with st.spinner("Overlaying Audio Track and rendering..."):
            video_clip = None
            audio_clip = None
            final_clip = None
            VIDEO_PATH = "background.mp4"
            
            # Setup dimensions based on selection
            if "9:16" in video_format:
                dimensions = (720, 1280)
            else:
                dimensions = (1280, 720)
                
            try:
                # Try loading the custom background video
                if os.path.exists(VIDEO_PATH) and os.path.getsize(VIDEO_PATH) > 0:
                    try:
                        video_clip = VideoFileClip(VIDEO_PATH)
                        if video_clip.duration < target_duration:
                            target_duration = video_clip.duration
                        video_clip = video_clip.subclip(0, target_duration)
                        st.info("🎥 Merging audio tracks with your custom background.mp4...")
                    except Exception as video_err:
                        st.warning("⚠️ Background video syntax issue. Defaulting to safe cinematic dark green canvas canvas fallback.")
                        video_clip = ColorClip(size=dimensions, color=(20, 50, 30), duration=target_duration)
                else:
                    st.warning("⚠️ 'background.mp4' not found. Rendering inside an emerald canvas background...")
                    video_clip = ColorClip(size=dimensions, color=(20, 50, 30), duration=target_duration)
                
                # Load the newly created AI voice asset
                audio_clip = AudioFileClip(audio_temp)
                if audio_clip.duration > target_duration:
                    audio_clip = audio_clip.subclip(0, target_duration)
                    
                # Bind components together
                final_clip = video_clip.set_audio(audio_clip)
                
                # Save out to output file container
                final_clip.write_videofile(
                    output_video_path,
                    codec="libx264",
                    audio_codec="aac",
                    fps=24,
                    logger=None
                )
                
                st.success("✨ Production Complete! Video fully built.")
                
                # Display output screen widgets
                with open(output_video_path, "rb") as video_file:
                    st.video(video_file.read())
                    
                with open(output_video_path, "rb") as video_file:
                    st.download_button(
                        label="📥 Download Video File",
                        data=video_file,
                        file_name=f"islamic_factory_{topic.lower().replace(' ', '_')}.mp4",
                        mime="video/mp4"
                    )
                    
            except Exception as e:
                st.error(f"❌ Production pipeline engine failed: {e}")
            finally:
                # Active background memory cleaner
                if video_clip: video_clip.close()
                if audio_clip: audio_clip.close()
                if final_clip: final_clip.close()
                
                if os.path.exists(audio_temp):
                    try:
                        os.remove(audio_temp)
                    except:
                        pass

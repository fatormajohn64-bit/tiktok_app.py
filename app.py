import os
import streamlit as st
from groq import Groq
from gtts import gTTS
from moviepy.editor import VideoFileClip, AudioFileClip, ColorClip

# --- PAGE SETUP ---
st.set_page_config(page_title="Islamic Video Content Factory PRO", page_icon="🌙", layout="wide")
st.title("🌙 Islamic Video Content Factory PRO")
st.caption("Generate unlimited cinematic Islamic videos using Groq & MoviePy.")

# --- API KEY INITIALIZATION ---
API_KEY = st.secrets.get("GROQ_API_KEY") or os.getenv("GROQ_API_KEY")

if not API_KEY:
    st.error("❌ KEY ERROR: 'GROQ_API_KEY' is missing from your Streamlit Secrets Management dashboard.")
    st.stop()

# Initialize Groq client
client = Groq(api_key=API_KEY)
st.success("✅ Connected Perfectly to Groq Network")

# --- SIDEBAR CONTROLS ---
st.sidebar.header("🎬 Cinematic Controls")
video_format = st.sidebar.selectbox("Aspect Ratio Layout", ["TikTok / Shorts (Vertical 9:16)", "YouTube (Horizontal 16:9)"])
chosen_length = st.sidebar.selectbox("Target Video Length", ["30 Seconds", "1 Minute", "2 Minutes"])
content_type = st.sidebar.selectbox("Select Theme", ["Motivational", "Historical Story / Seerah", "Quranic Reflection"])

duration_map = {"30 Seconds": 30, "1 Minute": 60, "2 Minutes": 120}
target_duration = duration_map[chosen_length]

topic = st.text_input("Video Topic", placeholder="Example: Tawakkul in Islam")

if st.button("Generate Cinematic Islamic Video"):
    if not topic:
        st.warning("⚠️ Please provide a video topic first.")
    else:
        st.info("Step 1: Compiling Narration Script via Groq...")
        
        system_instruction = (
            "You are an elite, highly academic Islamic scholar, historian, and cinematic scriptwriter. "
            "You have complete access to the expansive depth of authentic Hadith collections, Quranic context, and Seerah. "
            "CRUCIAL: Use deeply diverse vocabulary, varied emotional hooks, and unique narrative structures. "
            "IMPORTANT: Output ONLY the spoken narration text. Do not include scene labels, camera directions, brackets, or titles."
        )

        user_prompt = f"Write a powerful, deeply moving narration script about '{topic}' for a {chosen_length} {content_type} video."

        try:
            completion = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": system_instruction},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.85,
            )
            script_text = completion.choices[0].message.content
            
            st.subheader("📋 Generated Script:")
            st.write(script_text)
            
        except Exception as e:
            st.error(f"❌ Groq Generation Failed: {e}")
            st.stop()

        # --- STEP 2: VOICE SYNTHESIS ---
        current_dir = os.getcwd()
        audio_temp = os.path.join(current_dir, "voiceover.mp3")
        output_video_path = os.path.join(current_dir, "final_output.mp4")

        with st.spinner("Step 2: Synthesizing Voiceover..."):
            try:
                tts = gTTS(text=script_text, lang='en', slow=False)
                tts.save(audio_temp)
            except Exception as e:
                st.error(f"❌ Voice synthesis failed: {e}")
                st.stop()

        # --- STEP 3: VIDEO COMPILATION ENGINE ---
        with st.spinner("Step 3: Rendering Video & Overlaying Audio..."):
            video_clip = None
            audio_clip = None
            final_clip = None
            
            # Look for both options to be entirely safe
            VIDEO_PATH = None
            possible_names = ["background.mp4", "beautybeautyofkabbahforyoupagefypblackeditsallahua_1778788911723.mp4"]
            for name in possible_names:
                if os.path.exists(name) and os.path.getsize(name) > 0:
                    VIDEO_PATH = name
                    break
            
            if "Vertical" in video_format:
                dimensions = (720, 1280)
            else:
                dimensions = (1280, 720)

            try:
                # Load voice track first to find exact length
                audio_clip = AudioFileClip(audio_temp)
                audio_duration = audio_clip.duration
                
                # Cap duration to user selection
                final_duration = min(audio_duration, target_duration)
                
                # Trim audio to exact final duration
                audio_clip = audio_clip.subclip(0, final_duration)
                
                # Process the background video file if found
                if VIDEO_PATH:
                    try:
                        st.info(f"🎥 Found background clip: '{VIDEO_PATH}'. Processing...")
                        raw_video = VideoFileClip(VIDEO_PATH)
                        
                        # Handle clip wrapping/subclipping safely
                        if raw_video.duration < final_duration:
                            final_duration = raw_video.duration
                            audio_clip = audio_clip.subclip(0, final_duration)
                        
                        video_clip = raw_video.subclip(0, final_duration).resize(newsize=dimensions)
                    except Exception as video_err:
                        st.warning("⚠️ Background video format unreadable by server ffmpeg engine. Using deep canvas fallback...")
                        video_clip = ColorClip(size=dimensions, color=(15, 35, 23), duration=final_duration)
                else:
                    st.warning("⚠️ No valid video file detected in repository. Creating a deep cinematic green frame asset...")
                    video_clip = ColorClip(size=dimensions, color=(15, 35, 23), duration=final_duration)
                
                # Force video asset to register frames properly
                video_clip = video_clip.set_duration(final_duration)
                
                # Bind components together
                final_clip = video_clip.set_audio(audio_clip)
                
                # Render using precise format flags for mobile playback compatibility
                final_clip.write_videofile(
                    output_video_path, 
                    codec="libx264", 
                    audio_codec="aac", 
                    fps=24,
                    preset="medium",
                    ffmpeg_params=["-pix_fmt", "yuv420p"], # Forces standard pixel tracking layout so it never displays black
                    logger=None
                )
                
                # Confirming output container generation status
                if os.path.exists(output_video_path) and os.path.getsize(output_video_path) > 0:
                    st.success("✨ Production Complete! Video fully built.")
                    
                    # Read bytes directly to bypass caching blocks
                    with open(output_video_path, "rb") as file:
                        video_bytes = file.read()
                        st.video(video_bytes)
                        
                    st.download_button(
                        label="📥 Download Finished Video",
                        data=video_bytes,
                        file_name=f"islamic_factory_{topic.lower().replace(' ', '_')}.mp4",
                        mime="video/mp4"
                    )
                else:
                    st.error("❌ Output video file container was generated but is empty.")
                
            except Exception as e:
                st.error(f"❌ Production Engine Failure: {e}")
            finally:
                # Flush pipeline memories cleanly
                if video_clip: video_clip.close()
                if audio_clip: audio_clip.close()
                if final_clip: final_clip.close()
                
                if os.path.exists(audio_temp):
                    try:
                        os.remove(audio_temp)
                    except:
                        pass

import os
import subprocess
import streamlit as st
from gtts import gTTS
import cv2
import numpy as np

# Clear-cut check to prevent cache import overlap
try:
    from groq import Groq
    HAS_GROQ = True
except ModuleNotFoundError:
    HAS_GROQ = False

# --- PAGE SETUP ---
st.set_page_config(page_title="Islamic Video Content Factory PRO", page_icon="🌙", layout="wide")
st.title("🌙 Islamic Video Content Factory PRO")
st.caption("Generate unlimited cinematic Islamic videos using Groq & High-Speed Engines.")

# --- CHECK DEPENDENCIES ---
if not HAS_GROQ:
    st.error("📥 Streamlit is rebuilding the environment dependencies. Please refresh this page in 30 seconds!")
    st.stop()

# --- API KEY INITIALIZATION ---
API_KEY = st.secrets.get("GROQ_API_KEY") or os.getenv("GROQ_API_KEY")

if not API_KEY:
    st.error("❌ KEY ERROR: 'GROQ_API_KEY' is missing from your Streamlit Secrets.")
    st.info("Please add GROQ_API_KEY = 'your_gsk_key' to your Streamlit Advanced Secrets dashboard.")
    st.stop()

# Initialize the Groq Engine
try:
    client = Groq(api_key=API_KEY)
    st.success("✅ Connected Perfectly to Groq Network")
except Exception as e:
    st.error(f"❌ Failed to connect to Groq: {e}")
    st.stop()

# --- SIDEBAR CONTROLS ---
st.sidebar.header("🎬 Cinematic Controls")
video_format = st.sidebar.selectbox("Aspect Ratio Layout", ["TikTok / Shorts (Vertical 9:16)", "YouTube (Horizontal 16:9)"])
chosen_length = st.sidebar.selectbox("Target Video Length", ["30 Seconds", "1 Minute"])

duration_map = {"30 Seconds": 30, "1 Minute": 60}
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
            "CRUCIAL: Use deeply diverse vocabulary, varied emotional hooks, and unique narrative structures so that scripts never repeat phrases. "
            "IMPORTANT: Output ONLY the spoken narration text. Do not include scene labels, brackets, notes, or titles."
        )

        user_prompt = f"Write a powerful, deeply moving narration script about '{topic}' for a {chosen_length} video."

        try:
            # Using llama-3.3-70b-versatile for high quality reasoning
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
        video_temp = os.path.join(current_dir, "silent_video.mp4")
        output_video_path = os.path.join(current_dir, "final_output.mp4")

        with st.spinner("Step 2: Creating AI Voiceover..."):
            try:
                tts = gTTS(text=script_text, lang='en', slow=False)
                tts.save(audio_temp)
            except Exception as e:
                st.error(f"❌ Voice synthesis failed: {e}")
                st.stop()

        # --- STEP 3: HIGH-SPEED OPENCV RENDERING ---
        with st.spinner("Step 3: Processing Background Video Assets..."):
            VIDEO_PATH = "background.mp4"
            fps = 24
            total_frames = int(target_duration * fps)
            
            if "Vertical" in video_format:
                width, height = 540, 960  # Optimized resolution for blazing fast mobile cloud compilation
            else:
                width, height = 960, 540

            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            out_writer = cv2.VideoWriter(video_temp, fourcc, fps, (width, height))

            if os.path.exists(VIDEO_PATH) and os.path.getsize(VIDEO_PATH) > 0:
                st.info("🎥 Processing background.mp4 utilizing OpenCV processing channels...")
                cap = cv2.VideoCapture(VIDEO_PATH)
                
                frames_written = 0
                while frames_written < total_frames:
                    cap.set(cv2.CAP_PROP_POS_FRAMES, 0) # Seamlessly loop back if background clip is too short
                    while frames_written < total_frames:
                        ret, frame = cap.read()
                        if not ret:
                            break
                        resized_frame = cv2.resize(frame, (width, height), interpolation=cv2.INTER_NEAREST)
                        out_writer.write(resized_frame)
                        frames_written += 1
                cap.release()
            else:
                st.warning("⚠️ 'background.mp4' not found. Rendering deep emerald fallback sequences...")
                for _ in range(total_frames):
                    frame = np.zeros((height, width, 3), dtype=np.uint8)
                    frame[:] = [23, 35, 15] # Elegant dark green color space
                    out_writer.write(frame)
            
            out_writer.release()

        # --- STEP 4: HARDWARE-LEVEL FFMPEG AUDIO STITCHING ---
        with st.spinner("Step 4: Compiling Audio Tracks and Finalizing Video Export..."):
            try:
                if os.path.exists(output_video_path):
                    os.remove(output_video_path)
                
                ffmpeg_cmd = [
                    "ffmpeg", "-y",
                    "-i", video_temp,
                    "-i", audio_temp,
                    "-c:v", "libx264",
                    "-c:a", "aac",
                    "-map", "0:v:0",
                    "-map", "1:a:0",
                    "-shortest",
                    "-pix_fmt", "yuv420p",
                    "-preset", "ultrafast",  # Forces hardware level render instantly
                    output_video_path
                ]
                
                subprocess.run(ffmpeg_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
                
                if os.path.exists(output_video_path) and os.path.getsize(output_video_path) > 0:
                    st.success("✨ Production Complete! Video fully built.")
                    
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
                    st.error("❌ Final compilation error: Output container empty.")
                    
            except Exception as e:
                st.error(f"❌ Final Stitching Error: {e}")
            finally:
                # Local directory memory flush
                for temp_asset in [video_temp, audio_temp]:
                    if os.path.exists(temp_asset):
                        try:
                            os.remove(temp_asset)
                        except:
                            pass

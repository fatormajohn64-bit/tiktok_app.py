import os
import subprocess
import streamlit as st
from groq import Groq
from gtts import gTTS
import cv2
import numpy as np

# --- PAGE CONFIG ---
st.set_page_config(page_title="Islamic Video Factory Ultimate", page_icon="🌙", layout="wide")
st.title("🌙 Islamic Video Factory Ultimate")
st.caption("High-Speed Cinematic Content Generation powered by Groq & OpenCV Engine.")

# --- API KEY DETECTION ---
API_KEY = st.secrets.get("GROQ_API_KEY") or os.getenv("GROQ_API_KEY")

if not API_KEY:
    st.error("❌ KEY ERROR: 'GROQ_API_KEY' is completely missing from your Streamlit Secrets.")
    st.info("Please log into your Streamlit Cloud Dashboard, go to your app settings -> Secrets, and add it.")
    st.stop()

# Initialize Groq Client safely
try:
    client = Groq(api_key=API_KEY)
except Exception as e:
    st.error(f"❌ Initialization Failed: {e}")
    st.stop()

# --- INTERFACE DESIGN ---
st.sidebar.header("🎬 Video Configurations")
video_format = st.sidebar.selectbox("Layout Format", ["TikTok / Shorts (Vertical 9:16)", "YouTube (Horizontal 16:9)"])
chosen_length = st.sidebar.selectbox("Duration Target", ["30 Seconds", "1 Minute"])

duration_map = {"30 Seconds": 30, "1 Minute": 60}
target_duration = duration_map[chosen_length]

topic = st.text_input("Enter Video Topic", placeholder="e.g., The Beauty of Sabr (Patience)")

if st.button("Generate Cinematic Islamic Video", type="primary"):
    if not topic:
        st.warning("⚠️ Please enter a topic first.")
    else:
        st.info("⚡ Step 1: Requesting cinematic script from Groq Engine...")
        
        system_instruction = (
            "You are an elite Islamic cinematic scriptwriter. "
            "Output ONLY the spoken narration text. Do not include scene descriptions, directions, or brackets."
        )
        user_prompt = f"Write a deeply moving, motivational narration script about '{topic}' for a {chosen_length} video."

        try:
            completion = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": system_instruction},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.75,
            )
            script_text = completion.choices[0].message.content
            st.subheader("📋 Generated Narration Script:")
            st.success(script_text)
        except Exception as e:
            st.error(f"❌ Groq Generation Failed: {e}")
            st.info("💡 Tip: Double-check that your GROQ_API_KEY in Streamlit secrets is correct and hasn't expired!")
            st.stop()

        # --- SETUP PATHS ---
        current_dir = os.getcwd()
        audio_temp = os.path.join(current_dir, "voiceover.mp3")
        video_temp = os.path.join(current_dir, "silent_video.mp4")
        output_video_path = os.path.join(current_dir, "final_output.mp4")

        # Scan for ANY background video file uploaded to GitHub
        detected_video = None
        for file in os.listdir(current_dir):
            if file.lower().endswith(('.mp4', '.mov', '.avi')) and file not in ["silent_video.mp4", "final_output.mp4"]:
                detected_video = file
                break

        # --- STEP 2: TTS GENERATION ---
        with st.spinner("🎙️ Step 2: Generating AI Voiceover narration..."):
            try:
                tts = gTTS(text=script_text, lang='en', slow=False)
                tts.save(audio_temp)
            except Exception as e:
                st.error(f"❌ Voice synthesis failed: {e}")
                st.stop()

        # --- STEP 3: OPENCV RENDERING ---
        with st.spinner("🎥 Step 3: Looping and processing background frames..."):
            fps = 24
            total_frames = int(target_duration * fps)
            width, height = (540, 960) if "Vertical" in video_format else (960, 540)

            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            out_writer = cv2.VideoWriter(video_temp, fourcc, fps, (width, height))

            if detected_video and os.path.getsize(detected_video) > 0:
                st.info(f"🎞️ Using background asset file: '{detected_video}'")
                cap = cv2.VideoCapture(detected_video)
                frames_written = 0
                while frames_written < total_frames:
                    cap.set(cv2.CAP_PROP_POS_FRAMES, 0) # Restart loop seamlessly
                    while frames_written < total_frames:
                        ret, frame = cap.read()
                        if not ret:
                            break
                        resized = cv2.resize(frame, (width, height), interpolation=cv2.INTER_LINEAR)
                        out_writer.write(resized)
                        frames_written += 1
                cap.release()
            else:
                st.warning("⚠️ No background asset detected. Generating fallback deep emerald backdrop...")
                for _ in range(total_frames):
                    frame = np.zeros((height, width, 3), dtype=np.uint8)
                    frame[:] = [20, 40, 20] # Beautiful deep Islamic emerald green
                    out_writer.write(frame)
            out_writer.release()

        # --- STEP 4: FFMPEG AUDIO STITCHING ---
        with st.spinner("🎬 Step 4: Merging tracks into final video production..."):
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
                    "-preset", "ultrafast",
                    output_video_path
                ]
                subprocess.run(ffmpeg_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
                
                if os.path.exists(output_video_path) and os.path.getsize(output_video_path) > 0:
                    st.success("✨ Video Compiled Successfully!")
                    with open(output_video_path, "rb") as file:
                        video_bytes = file.read()
                        st.video(video_bytes)
                    
                    st.download_button(
                        label="📥 Download Finished Video",
                        data=video_bytes,
                        file_name=f"islamic_factory_{topic.lower().replace(' ', '_')}.mp4",
                        mime="video/mp4"
                    )
            except Exception as e:
                st.error(f"❌ Audio/Video merging failed: {e}")
            finally:
                # Direct cleanup of staging files
                for f in [video_temp, audio_temp]:
                    if os.path.exists(f):
                        try: os.remove(f)
                        except: pass

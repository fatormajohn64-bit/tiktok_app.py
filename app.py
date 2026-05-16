import os
import subprocess
import streamlit as st
import google.generativeai as genai
from gtts import gTTS
import cv2
import numpy as np

# --- PAGE SETUP ---
st.set_page_config(page_title="Islamic Video Factory Ultimate", page_icon="🌙", layout="wide")
st.title("🌙 Islamic Video Factory Ultimate")
st.caption("Generate cinematic Islamic videos using Gemini & Optimized Rendering Engines.")

# --- API KEY INITIALIZATION ---
API_KEY = (
    st.secrets.get("GEMINI_API_KEY") or 
    st.secrets.get("GROQ_API_KEY") or 
    os.getenv("GEMINI_API_KEY")
)

if not API_KEY:
    st.error("❌ KEY ERROR: Please add your API Key to your Streamlit Secrets dashboard.")
    st.stop()

genai.configure(api_key=API_KEY)

# --- SIDEBAR CONTROLS ---
st.sidebar.header("🎬 Cinematic Controls")
video_format = st.sidebar.selectbox("Aspect Ratio Layout", ["TikTok / Shorts (Vertical 9:16)", "YouTube (Horizontal 16:9)"])
chosen_length = st.sidebar.selectbox("Target Video Length", ["30 Seconds", "1 Minute"])

duration_map = {"30 Seconds": 30, "1 Minute": 60}
target_duration = duration_map[chosen_length]

topic = st.text_input("Video Topic", placeholder="Example: Sabr and Rewards")

if st.button("Generate Cinematic Islamic Video"):
    if not topic:
        st.warning("⚠️ Please provide a video topic first.")
    else:
        st.info("Step 1: Requesting short cinematic script via Gemini...")
        
        system_instruction = (
            "You are an elite Islamic scriptwriter. Output ONLY the spoken narration text. "
            "CRUCIAL: Keep the script concise, exactly fitting the requested duration when spoken. "
            "Do not include brackets, titles, scene numbers, or descriptions."
        )
        user_prompt = f"Write a powerful, short spoken narration text about '{topic}' for a {chosen_length} video."

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
            st.error(f"❌ Rate Limit or API Error: Please wait 60 seconds and try again. ({e})")
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
                width, height = 540, 960  # Optimized dimensions for faster mobile cloud rendering
            else:
                width, height = 960, 540

            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            out_writer = cv2.VideoWriter(video_temp, fourcc, fps, (width, height))

            if os.path.exists(VIDEO_PATH) and os.path.getsize(VIDEO_PATH) > 0:
                st.info("🎥 Processing your custom 'background.mp4'...")
                cap = cv2.VideoCapture(VIDEO_PATH)
                
                frames_written = 0
                while frames_written < total_frames:
                    cap.set(cv2.CAP_PROP_POS_FRAMES, 0) # Smooth loop if background is shorter than audio
                    while frames_written < total_frames:
                        ret, frame = cap.read()
                        if not ret:
                            break
                        resized_frame = cv2.resize(frame, (width, height), interpolation=cv2.INTER_NEAREST)
                        out_writer.write(resized_frame)
                        frames_written += 1
                cap.release()
            else:
                st.warning("⚠️ Background file unreadable. Rendering emergency backdrop...")
                for _ in range(total_frames):
                    frame = np.zeros((height, width, 3), dtype=np.uint8)
                    frame[:] = [23, 35, 15]
                    out_writer.write(frame)
            
            out_writer.release()

        # --- STEP 4: FAST AUDIO STITCHING ---
        with st.spinner("Step 4: Merging tracks into final layout..."):
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
                    "-preset", "ultrafast",  # Forces the server to build the video instantly
                    output_video_path
                ]
                
                subprocess.run(ffmpeg_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
                
                if os.path.exists(output_video_path) and os.path.getsize(output_video_path) > 0:
                    st.success("✨ Production Complete!")
                    
                    with open(output_video_path, "rb") as file:
                        st.video(file.read())
                        
                    st.download_button(
                        label="📥 Download Finished Video",
                        data=open(output_video_path, "rb"),
                        file_name="islamic_factory_video.mp4",
                        mime="video/mp4"
                    )
                
            except Exception as e:
                st.error(f"❌ Final Stitching Error: {e}")
            finally:
                for temp_asset in [video_temp, audio_temp]:
                    if os.path.exists(temp_asset):
                        try:
                            os.remove(temp_asset)
                        except:
                            pass

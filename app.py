import os
import streamlit as st
import google.generativeai as genai

st.set_page_config(page_title="Islamic AI Video Production", page_icon="🎬")
st.title("🎬 Islamic AI Video Production Line")

# API Setup
API_KEY = st.secrets.get("GEMINI_API_KEY") or os.getenv("GEMINI_API_KEY")
if not API_KEY:
    st.error("❌ API key missing in Streamlit Secrets!")
    st.stop()

genai.configure(api_key=API_KEY)

# --- SMART MODEL SELECTION ---
# This part automatically finds a working model so you don't get 404 errors
try:
    available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
    # Look for flash first, then pro, then just take the first one
    if any("flash" in m for m in available_models):
        MODEL_NAME = [m for m in available_models if "flash" in m][0]
    elif any("pro" in m for m in available_models):
        MODEL_NAME = [m for m in available_models if "pro" in m][0]
    else:
        MODEL_NAME = available_models[0]
    
    model = genai.GenerativeModel(MODEL_NAME)
    st.success(f"✅ Using Model: {MODEL_NAME}")
except Exception as e:
    st.error(f"❌ Could not find any available models: {e}")
    st.stop()

# --- VIDEO CHECK ---
VIDEO_PATH = "background.mp4"
if os.path.exists(VIDEO_PATH):
    st.success("✅ background.mp4 detected")
else:
    st.warning("⚠️ background.mp4 not found in main folder.")

topic = st.text_input("Enter Islamic video topic:", placeholder="e.g. Patience in Islam")

if st.button("🚀 Start Production Line"):
    if not topic:
        st.warning("Please enter a topic.")
    else:
        with st.spinner("Generating script..."):
            try:
                prompt = f"Create a short, viral Islamic TikTok script about: {topic}. Include a Quran verse."
                response = model.generate_content(prompt)
                st.subheader("Generated Script:")
                st.write(response.text)
            except Exception as e:
                st.error(f"❌ Generation failed: {e}")

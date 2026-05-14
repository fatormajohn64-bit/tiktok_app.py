import streamlit as st
import google.generativeai as genai
import os

# --- 1. SECURE BRAIN SETUP ---
try:
    # This automatically grabs the key you just added to Streamlit Secrets
    if "GEMINI_API_KEY" in st.secrets:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        # Standard model name to fix the 404 error from your screenshots
        model = genai.GenerativeModel('gemini-1.5-flash')
    else:
        st.error("Key not found! Go to Streamlit Settings > Secrets and add: GEMINI_API_KEY = 'your_key'")
except Exception as e:
    st.error(f"Brain Connection Error: {e}")

# --- 2. THE FACTORY ---
st.title("🕌 Master Islamic AI Factory")
st.write("Ready to create your viral Kabbah post!")

if st.button("🚀 Generate Viral Content"):
    with st.spinner("AI is crafting the beauty..."):
        try:
            # Generate Text content
            prompt = "Generate 1 Islamic Theme | 1 Short Powerful Quote. Format: THEME | QUOTE"
            response = model.generate_content(prompt)
            parts = response.text.split("|")
            
            theme = parts[0].strip() if len(parts) > 0 else "Faith"
            quote = parts[1].strip() if len(parts) > 1 else response.text
            
            # Display Results
            st.success(f"**Theme:** {theme}")
            st.info(f"**Quote:** {quote}")
            
            # THE FIX: Looking for your exact Xender file name from your screenshot
            video_filename = "beautybeautyofkabbahforyoupagefypblackeditsallahua_1778788911723.mp4"
            
            if not os.path.exists(video_filename):
                st.warning(f"⚠️ Video file '{video_filename}' is not on GitHub yet!")
                st.write("👉 Upload your video from Xender to your GitHub repo to finish.")
            else:
                st.write("✅ Kabbah Video Found! Ready to create the post.")
                
        except Exception as e:
            # This captures the 404 error if the model name is still causing issues
            st.error(f"❌ AI Error: {e}")

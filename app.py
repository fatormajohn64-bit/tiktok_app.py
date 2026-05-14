import streamlit as st
import google.generativeai as genai
import os

# --- 1. SETUP ---
# Pulling the key safely from your Secrets
try:
    if "GEMINI_API_KEY" in st.secrets:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        # Using the absolute standard model name to stop 404 errors
        model = genai.GenerativeModel('gemini-1.5-flash')
    else:
        st.error("Missing API Key in Streamlit Secrets!")
except Exception as e:
    st.error(f"Brain Error: {e}")

# --- 2. THE APP ---
st.title("🕌 Master Islamic AI Factory")

if st.button("🚀 Generate New Content"):
    with st.spinner("AI is working..."):
        try:
            # Generate the text
            prompt = "Generate 1 Islamic Theme | 1 Short Power Quote. Format: THEME | QUOTE"
            response = model.generate_content(prompt)
            parts = response.text.split("|")
            
            theme = parts[0].strip()
            quote = parts[1].strip()
            
            # Show the "Beauty"
            st.success(f"**Theme:** {theme}")
            st.info(f"**Quote:** {quote}")
            
            # Check for the video from your Xender folder
            if not os.path.exists("background.mp4"):
                st.warning("⚠️ 'background.mp4' not found on GitHub. Video skipped, but text is ready!")
            else:
                st.write("✅ Video file found and ready for processing.")
                
        except Exception as e:
            st.error(f"❌ Connection Error: {e}")

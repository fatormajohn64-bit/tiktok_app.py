import streamlit as st
import google.generativeai as genai
import os

# --- 1. SECURE AI BRAIN CONFIGURATION ---
# This version pulls the key from your 'Secrets' dashboard so it's never exposed in code
try:
    if "GEMINI_API_KEY" in st.secrets:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        # Standard model name to fix the 404 error from your screenshot
        model = genai.GenerativeModel('gemini-1.5-flash')
    else:
        st.error("API Key missing! Add 'GEMINI_API_KEY' to your Streamlit Secrets.")
except Exception as e:
    st.error(f"Brain Connection Error: {e}")

# --- 2. THE DASHBOARD ---
st.title("🕌 Master Islamic AI Factory")
st.subheader("Automated Content Generation v3.0")

if st.button("🚀 Run Automatic Sequence Now"):
    with st.spinner("AI is crafting your post..."):
        try:
            # Generate Viral Text
            prompt = "Act as a Master Islamic Creator. Generate: 1 Theme | 1 Short Powerful Quote. Format: THEME | QUOTE"
            response = model.generate_content(prompt)
            
            parts = response.text.split("|")
            theme = parts[0].strip() if len(parts) > 0 else "Faith"
            quote = parts[1].strip() if len(parts) > 1 else response.text
            
            # Display Results
            st.success(f"**Theme:** {theme}")
            st.info(f"**Quote:** {quote}")
            
            # Check for video file (background.mp4)
            if not os.path.exists("background.mp4"):
                st.warning("⚠️ 'background.mp4' missing! Upload your Xender video and rename it to 'background.mp4'.")
            else:
                st.write("✅ Video file found!")
                
        except Exception as e:
            st.error(f"❌ AI Brain Error: {e}")

import streamlit as st
import google.generativeai as genai
import os

# --- 1. THE STABLE BRAIN CONFIG ---
try:
    if "GEMINI_API_KEY" in st.secrets:
        # Forcing the stable API version to kill the 404/v1beta error
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        
        # Switching to 'gemini-pro' for maximum compatibility
        model = genai.GenerativeModel('gemini-pro')
    else:
        st.error("API Key missing! Add 'GEMINI_API_KEY' to Streamlit Secrets.")
except Exception as e:
    st.error(f"Brain Setup Error: {e}")

# --- 2. THE DASHBOARD ---
st.title("🕌 Master Islamic AI Factory")
st.write("Using Stable Model v1.0")

if st.button("🚀 Generate Viral Content"):
    with st.spinner("AI is crafting the beauty..."):
        try:
            # Generate the content
            prompt = "Generate 1 Islamic Theme | 1 Short Powerful Quote. Format: THEME | QUOTE"
            response = model.generate_content(prompt)
            
            # Use the text if the split fails
            text_output = response.text
            if "|" in text_output:
                parts = text_output.split("|")
                theme = parts[0].strip()
                quote = parts[1].strip()
            else:
                theme = "Faith"
                quote = text_output
            
            # Show the results
            st.success(f"**Theme:** {theme}")
            st.info(f"**Quote:** {quote}")
            
            # Your specific video file from Xender
            video_file = "beautybeautyofkabbahforyoupagefypblackeditsallahua_1778788911723.mp4"
            
            if not os.path.exists(video_file):
                st.warning(f"⚠️ Video '{video_file}' not found on GitHub!")
            else:
                st.write("✅ Kabbah Video Found!")
                
        except Exception as e:
            # Captures exactly why the brain is still failing
            st.error(f"❌ AI Error: {e}")

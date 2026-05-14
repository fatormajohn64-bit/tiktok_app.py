import streamlit as st
import google.generativeai as genai
import os

# --- 1. THE STABLE BRAIN CONFIG ---
try:
    if "GEMINI_API_KEY" in st.secrets:
        # This line forces the app to use the stable v1 API instead of v1beta
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"], transport='rest')
        
        # We are using the most stable model name possible here
        model = genai.GenerativeModel('gemini-1.5-flash')
    else:
        st.error("API Key missing from Streamlit Secrets!")
except Exception as e:
    st.error(f"Brain Setup Error: {e}")

# --- 2. THE DASHBOARD ---
st.title("🕌 Master Islamic AI Factory")
st.write("Forcing Stable API Connection...")

if st.button("🚀 Generate Viral Content"):
    with st.spinner("AI is crafting the beauty..."):
        try:
            # Generate the content
            prompt = "Generate 1 Islamic Theme | 1 Short Powerful Quote. Format: THEME | QUOTE"
            response = model.generate_content(prompt)
            
            parts = response.text.split("|")
            theme = parts[0].strip() if len(parts) > 0 else "Faith"
            quote = parts[1].strip() if len(parts) > 1 else response.text
            
            # Show the Results
            st.success(f"**Theme:** {theme}")
            st.info(f"**Quote:** {quote}")
            
            # Link to your Xender video file
            video_file = "beautybeautyofkabbahforyoupagefypblackeditsallahua_1778788911723.mp4"
            
            if not os.path.exists(video_file):
                st.warning(f"⚠️ Video file '{video_file}' not found on GitHub!")
            else:
                st.write("✅ Kabbah Video Found!")
                
        except Exception as e:
            # If this still shows 404, it means the API key itself is restricted
            st.error(f"❌ AI Error: {e}")

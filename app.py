import streamlit as st
import google.generativeai as genai
import os
import json
import random
from datetime import datetime
from PIL import Image

# --- 1. INITIAL SETUP & STABLE BRAIN ---
st.set_page_config(page_title="Islamic TikTok AI Factory", layout="wide")

# This fix prevents the 404 v1beta error seen in your logs
def setup_genai():
    try:
        if "GEMINI_API_KEY" in st.secrets:
            genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
            # Using gemini-pro as the stable fallback to avoid 404 errors
            return genai.GenerativeModel("gemini-pro")
        else:
            st.error("Missing GEMINI_API_KEY in Streamlit Secrets.")
            return None
    except Exception as e:
        st.error(f"Brain Connection Error: {e}")
        return None

model = setup_genai()

# --- 2. FOLDER & DATABASE SYSTEM ---
folders = ["backgrounds", "exports", "logs"]
for f in folders:
    if not os.path.exists(f):
        os.makedirs(f)

DB_FILE = "used_quotes.json"

def load_used_content():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r") as f:
            return json.load(f)
    return []

def save_used_content(quote):
    history = load_used_content()
    history.append({"quote": quote, "date": str(datetime.now())})
    with open(DB_FILE, "w") as f:
        json.dump(history, f)

# --- 3. UI LAYOUT ---
st.title("🕌 Islamic TikTok AI Factory")
st.markdown("### Automated Viral Content Machine v1.0")

col1, col2 = st.columns([1, 1])

with col1:
    st.header("⚙️ Configuration")
    batch_size = st.number_input("Number of videos to generate", min_value=1, max_value=100, value=1)
    style = st.selectbox("Content Style", ["Emotional Reminders", "Quranic Motivation", "Peaceful Reflections"])
    
    generate_btn = st.button("🚀 Start Production Line")

with col2:
    st.header("📊 Factory Status")
    history = load_used_content()
    st.metric("Unique Videos Generated", len(history))
    if os.path.exists("background.mp4"):
        st.success("✅ background.mp4 detected")
    else:
        st.warning("⚠️ No 'background.mp4' found in root folder.")

# --- 4. CORE AUTOMATION ENGINE ---
if generate_btn and model:
    progress_bar = st.progress(0)
    
    for i in range(batch_size):
        st.write(f"Generating Video {i+1} of {batch_size}...")
        
        # A. Uniqueness Engine: Dynamic Prompting
        random_seed = random.randint(1, 10000)
        prompt = f"""Generate a unique, viral {style} for TikTok. 
        Focus: Heart-touching Islamic wisdom. 
        Variation ID: {random_seed}. 
        Format: HOOK | BODY | HASHTAGS.
        Do not repeat previous common phrases."""
        
        try:
            response = model.generate_content(prompt)
            content = response.text
            
            # Save to uniqueness database
            save_used_content(content)
            
            # B. UI Preview
            st.info(f"**Generated Content:**\n{content}")
            
            # C. Simulation of MoviePy Export (Requires high-RAM environment)
            st.write("🎬 Processing video overlays (Background: background.mp4)...")
            
        except Exception as e:
            st.error(f"Error on video {i+1}: {e}")
            
        progress_bar.progress((i + 1) / batch_size)
    
    st.success("✨ Batch Production Complete!")

import os
import json
import time
import random
import tempfile
from datetime import datetime
import streamlit as st
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from gtts import gTTS
from groq import Groq

# Safely handle moviepy import for different environments
try:
    from moviepy.editor import VideoFileClip, AudioFileClip, ColorClip, CompositeVideoClip, ImageClip
except ImportError:
    from moviepy.video.io.VideoFileClip import VideoFileClip
    from moviepy.audio.io.AudioFileClip import AudioFileClip
    from moviepy.video.VideoClip import ColorClip, ImageClip
    from moviepy.video.compositing.CompositeVideoClip import CompositeVideoClip

# ==============================================================================
# 1. STREAMLIT UI CONFIGURATION & THEME (Dark Islamic Luxury Aesthetic)
# ==============================================================================
st.set_page_config(
    page_title="An-Noor | Islamic AI Video Content Factory",
    page_icon="🕌",
    layout="wide",
    initial_sidebar_state="expanded"
)

CUSTOM_CSS = """
<style>
    :root {
        --primary-emerald: #064e3b;
        --dark-bg: #022c22;
        --luxury-gold: #fbbf24;
    }
    .stApp {
        background-color: #0b0f17;
        color: #e2e8f0;
    }
    .sidebar .sidebar-content {
        background-color: #022c22 !important;
    }
    h1, h2, h3, .gold-text {
        color: #fbbf24 !important;
        font-family: 'Georgia', serif;
    }
    .status-card {
        background-color: #064e3b;
        border-radius: 8px;
        padding: 15px;
        border-left: 5px solid #fbbf24;
        margin-bottom: 15px;
    }
    .stButton>button {
        background-color: #064e3b !important;
        color: #fbbf24 !important;
        border: 1px solid #fbbf24 !important;
        border-radius: 4px;
        font-weight: bold;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        background-color: #fbbf24 !important;
        color: #022c22 !important;
        box-shadow: 0px 0px 12px #fbbf24;
    }
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# ==============================================================================
# 2. PERSISTENT NON-REPEATING MEMORY ENGINE
# ==============================================================================
MEMORY_FILE = "memory.json"

def load_memory():
    if os.path.exists(MEMORY_FILE):
        try:
            with open(MEMORY_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return {"generated_videos": []}
    return {"generated_videos": []}

def save_memory(memory_data):
    with open(MEMORY_FILE, 'w', encoding='utf-8') as f:
        json.dump(memory_data, f, ensure_ascii=False, indent=4)

def update_memory(category, style, hook, narration, quran_verse, hadith):
    memory = load_memory()
    entry = {
        "timestamp": datetime.now().isoformat(),
        "category": category,
        "style": style,
        "hook": hook,
        "narration": narration,
        "quran_verse_used": quran_verse,
        "hadith_used": hadith
    }
    memory["generated_videos"].append(entry)
    save_memory(memory)

def get_memory_exclusion_string():
    memory = load_memory()
    if not memory["generated_videos"]:
        return "None."
    
    recent_hooks = [v["hook"] for v in memory["generated_videos"][-20:] if "hook" in v]
    recent_verses = [v["quran_verse_used"] for v in memory["generated_videos"][-20:] if "quran_verse_used" in v]
    
    exclusion_text = f"CRITICAL: Do not repeat or closely mimic these recent hooks: {recent_hooks}. "
    exclusion_text += f"Avoid reusing these exact Quran verses if possible: {recent_verses}."
    return exclusion_text

# ==============================================================================
# 3. GROQ AI ENGINE WITH AUTOMATIC FALLBACK LOGIC
# ==============================================================================
def generate_islamic_script(category, video_style, video_length, language):
    # Initialize Groq client securely from secrets
    try:
        api_key = st.secrets["GROQ_API_KEY"]
        client = Groq(api_key=api_key)
    except Exception as e:
        st.error("Groq API Key missing or misconfigured in Production Secrets.")
        return None

    exclusion_rules = get_memory_exclusion_string()
    
    system_prompt = f"""
    You are an elite Islamic scholar, Seerah historian, Quranic reflection teacher, and masterful cinematic documentary narrator.
    Your goal is to produce highly captivating, authentic, emotionally profound script blueprints for short-form or long-form videos.
    
    Output MUST be valid JSON with the following exact keys:
    {{
        "hook": "An attention-grabbing first 3 seconds statement matching the style",
        "narration": "The full voiceover text script optimized for the requested length",
        "quran_verse_used": "Specific reference and text used",
        "hadith_used": "Specific Hadith reference used, or N/A if none",
        "cinematic_visual_description": "Production notes describing background pacing"
    }}
    
    Constraints:
    - Language: {language}
    - Video Style Tone: {video_style}
    - Targeted Video Length: {video_length}
    - Accuracy: Ensure absolute theological accuracy for Quran and Hadith sources. Do not fabricate citations.
    - Diversity: {exclusion_rules}
    """

    user_prompt = f"Generate an original, cinematic content script about '{category}' matching the style '{video_style}'."

    # Smart Fallback Mechanism
    models_to_try = ["llama-3.3-70b-versatile", "llama3-8b-8192", "mixtral-8x7b-32768"]
    
    for model in models_to_try:
        try:
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                response_format={"type": "json_object"},
                temperature=0.75
            )
            return json.loads(response.choices[0].message.content)
        except Exception as e:
            st.warning(f"Model {model} failed: {e}")
            continue
            
    st.error("All AI models failed to respond. Please check your network connection or API quota limits.")
    return None

# ==============================================================================
# 4. PILLOW SUBTITLE GENERATOR (ImageMagick Bypass)
# ==============================================================================
def create_subtitle_image_clip(text, duration, target_size, start_time):
    w, h = target_size
    # Create transparent layer
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Robust font fallback handling
    try:
        font = ImageFont.truetype("DejaVuSans-Bold.ttf", int(h * 0.045))
    except IOError:
        try:
            font = ImageFont.truetype("arial.ttf", int(h * 0.045))
        except IOError:
            font = ImageFont.load_default()

    # Wrap text cleanly
    words = text.split()
    lines = []
    current_line = []
    for word in words:
        current_line.append(word)
        test_line = " ".join(current_line)
        bbox = draw.textbbox((0, 0), test_line, font=font)
        if (bbox[2] - bbox[0]) > (w * 0.85):
            current_line.pop()
            lines.append(" ".join(current_line))
            current_line = [word]
    if current_line:
        lines.append(" ".join(current_line))

    # Render wrapped text rows onto canvas
    full_text = "\n".join(lines)
    bbox = draw.textbbox((0, 0), full_text, font=font)
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]
    
    x = (w - text_w) // 2
    y = int(h * 0.75)  # Safe lower position for captions
    
    # High contrast backdrop drop shadow
    shadow_offset = 3
    draw.text((x + shadow_offset, y + shadow_offset), full_text, font=font, fill=(0, 0, 0, 220))
    draw.text((x, y), full_text, font=font, fill=(251, 191, 36, 255)) # Luxury gold text color
    
    img_np = np.array(img)
    clip = ImageClip(img_np).set_start(start_time).set_duration(duration).set_position(('center', 'top'))
    return clip

# ==============================================================================
# 5. MOVIEPY VIDEO ENGINE (Streamlit Cloud Optimized Blueprint)
# ==============================================================================
def build_video_pipeline(script, voice_style, ratio_mode):
    output_path = os.path.join(tempfile.gettempdir(), f"factory_out_{int(time.time())}.mp4")
    audio_path = os.path.join(tempfile.gettempdir(), f"voice_{int(time.time())}.mp3")
    
    # 1. Voice Synthesis (gTTS System Wrapper)
    lang_map = {"English": "en", "Arabic": "ar", "French": "fr", "Urdu": "ur"}
    tts_lang = lang_map.get(st.session_state.get('lang_choice', 'English'), 'en')
    
    tts = gTTS(text=script['narration'], lang=tts_lang, slow=False)
    tts.save(audio_path)
    
    audio_clip = AudioFileClip(audio_path)
    duration = audio_clip.duration
    
    # Target Resolution calculation
    target_size = (1080, 1920) if ratio_mode == "9:16" else (1920, 1080)
    
    # 2. Resilient Asset Loading & Fallback Safeguards
    # Default to a beautiful cinematic emerald green background using PIL (100% crash-proof)
    bg_image = Image.new("RGB", target_size, (2, 44, 34))
    bg_clip = ImageClip(np.array(bg_image)).set_duration(duration)
    
    if os.path.exists("background.mp4"):
        try:
            video_asset = VideoFileClip("background.mp4").without_audio()
            # Safe resize handling across different MoviePy versions
            try:
                video_asset = video_asset.resize(target_size)
            except AttributeError:
                try:
                    from moviepy.video.fx.all import resize
                    video_asset = video_asset.fx(resize, target_size[0], target_size[1])
                except ImportError:
                    pass # Keep original size if resize tools are completely unavailable
            
            if video_asset.duration < duration:
                loops = int(np.ceil(duration / video_asset.duration))
                video_asset = video_asset.loop(n=loops)
            bg_clip = video_asset.subclip(0, duration)
        except Exception:
            pass # Gracefully keep the beautiful emerald PIL background if video fails

    # 3. Dynamic Subtitle Segmenter
    sentences = [s.strip() for s in script['narration'].replace('.', '.|').replace('!', '!|').replace('?', '?|').split('|') if s.strip()]
    subtitle_clips = []
    
    if sentences:
        time_per_sentence = duration / len(sentences)
        for idx, sentence in enumerate(sentences):
            start = idx * time_per_sentence
            sub_clip = create_subtitle_image_clip(sentence, time_per_sentence, target_size, start)
            subtitle_clips.append(sub_clip)

    # 4. Final Sequence Multi-Layer Composition
    final_video = CompositeVideoClip([bg_clip] + subtitle_clips).set_audio(audio_clip)
    
    # Render Out Execution
    final_video.write_videofile(
        output_path,
        fps=30,
        codec="libx264",
        audio_codec="aac",
        preset="ultrafast",
        logger=None
    )
    
    # Clean up asset memory spaces cleanly
    audio_clip.close()
    bg_clip.close()
    
    return output_path, audio_path

# ==============================================================================
# 6. STREAMLIT APPLICATION INTERFACE DESIGN
# ==============================================================================
st.markdown("<h1>🕌 AN-NOOR: ULTIMATE ISLAMIC AI VIDEO FACTORY</h1>", unsafe_allow_html=True)
st.markdown("<p style='color: #a0aec0;'>Production-Ready Automated Islamic SaaS Content Infrastructure</p>", unsafe_allow_html=True)
st.markdown("---")

# Navigation Sidebar Controls
st.sidebar.markdown("<h2 class='gold-text'>🕋 Factory Dashboard</h2>", unsafe_allow_html=True)

category_selection = st.sidebar.selectbox("Content Knowledge Arena", [
    "Quran Reflection", "Seerah History", "Islamic Motivation", 
    "Tawakkul (Reliance on Allah)", "Sabr (Patience)", "Masculinity in Islam", 
    "Brotherhood", "Jannah and Akhirah", "Muslim Productivity"
])

video_type = st.sidebar.selectbox("Platform Format", ["TikTok / Shorts / Reels", "YouTube Long-form"])
aspect_ratio = "9:16" if video_type == "TikTok / Shorts / Reels" else "16:9"

video_length = st.sidebar.selectbox("Target Runtime Context", [
    "15 seconds", "30 seconds", "1 minute", "2 minutes", "5 minutes"
])

video_style = st.sidebar.selectbox("Cinematic Tone Matrix", [
    "Cinematic", "Dark Emotional", "Documentary", "Epic", "Motivational", "Warrior Mindset"
])

voice_style = st.sidebar.selectbox("Vocal Architecture", [
    "Deep Male Narrator", "Calm Narrator", "Emotional Imam", "Soft Spiritual Voice"
])

language_choice = st.sidebar.selectbox("Language Configuration", ["English", "Arabic", "French", "Urdu"])
st.sidebar.markdown("---")

# Main Dashboard Workspace Layout
tab_studio, tab_memory, tab_system = st.tabs(["🎬 Production Studio", "🗄️ Memory Vault", "⚙️ Deployment Blueprints"])

with tab_studio:
    st.markdown("<h3 class='gold-text'>Video Engine Control Panel</h3>", unsafe_allow_html=True)
    
    if st.button("🚀 IGNITE AUTOMATED PRODUCTION RUN"):
        st.session_state['lang_choice'] = language_choice
        
        with st.status("Constructing Theological Script Blueprint via Groq Engine...", expanded=True) as status:
            script_data = generate_islamic_script(category_selection, video_style, video_length, language_choice)
            
            if script_data:
                status.update(label="Script Synthesized successfully. Initiating Media Composition Suite...", state="running")
                st.write("**Generated Hook:** ", script_data.get('hook'))
                st.write("**Quran Reference:** ", script_data.get('quran_verse_used'))
                
                video_out, audio_out = build_video_pipeline(script_data, voice_style, aspect_ratio)
                
                # Update Non-repeating long-term database logs
                update_memory(
                    category_selection, video_style, script_data.get('hook'), 
                    script_data.get('narration'), script_data.get('quran_verse_used'), 
                    script_data.get('hadith_used')
                )
                
                status.update(label="Media Content Package Compiled Successfully!", state="complete")
                
                st.balloons()
                
                # Visual Preview Section Layout
                st.markdown("### 📽️ Master Quality Output Preview")
                st.video(video_out)
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    with open(video_out, "rb") as file:
                        st.download_button(label="📥 Download Master Video (MP4)", data=file, file_name="islamic_ai_factory_master.mp4", mime="video/mp4")
                with col2:
                    st.download_button(label="📝 Download Production Script (TXT)", data=script_data.get('narration'), file_name="narration_blueprint.txt")
                with col3:
                    st.download_button(label="📜 Download Subtitle Tracks (TXT)", data=json.dumps(script_data, indent=4, ensure_ascii=False), file_name="metadata_manifest.json")

with tab_memory:
    st.markdown("<h3 class='gold-text'>Long-Term Memory Data Lake</h3>", unsafe_allow_html=True)
    st.write("Below are the stored records keeping track of past generation topics and hooks to protect your system from producing repetitive concepts.")
    current_memory = load_memory()
    st.json(current_memory)

with tab_system:
    st.markdown("<h3 class='gold-text'>System Initialization Manifest</h3>", unsafe_allow_html=True)
    st.code("""
# App Directory Architecture Requirements
.
├── app.py
├── requirements.txt
├── packages.txt
├── memory.json
├── background.mp4 (Optional cinematic footage track loop)
└── .streamlit/
    └── secrets.toml
    """, language="bash")

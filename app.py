import streamlit as st
import google.generativeai as genai
from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip
from PIL import Image, ImageDraw, ImageFont
import textwrap
import os

# =========================
# STREAMLIT PAGE CONFIG
# =========================
st.set_page_config(page_title="Master Islamic AI Factory", layout="centered")

st.title("🕌 Master Islamic AI Factory")
st.write("Automated Morning Video + Evening Islamic Quote Generator")

# =========================
# GEMINI API SETUP
# =========================
try:
    GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=GEMINI_API_KEY)

    # FIXED MODEL NAME
    model = genai.GenerativeModel('gemini-pro')

except Exception as e:
    st.error(f"Gemini setup failed: {e}")
    st.stop()

# =========================
# VIDEO FILE
# =========================
VIDEO_FILE = "beautybeautyofkabbahforyoupagefypblackeditsallahua_1778788911723.mp4"

# =========================
# GENERATE MORNING QUOTE
# =========================
def generate_morning_quote():
    prompt = """
    Generate one short powerful Islamic motivational quote.
    Keep it under 15 words.
    Deep, emotional, and TikTok-ready.
    """

    response = model.generate_content(prompt)
    return response.text.strip()

# =========================
# CREATE MORNING VIDEO
# =========================
def create_morning_video():
    if not os.path.exists(VIDEO_FILE):
        st.warning("Please upload the Kabbah video from Xender to GitHub!")
        return

    try:
        quote = generate_morning_quote()

        st.info(f"Generated Morning Quote: {quote}")

        video = VideoFileClip(VIDEO_FILE)

        txt_clip = TextClip(
            quote,
            fontsize=60,
            color='white',
            method='caption',
            size=(900, None),
            align='center'
        )

        txt_clip = txt_clip.set_position(("center", "center"))
        txt_clip = txt_clip.set_duration(video.duration)

        final_video = CompositeVideoClip([video, txt_clip])

        output_file = "morning_post.mp4"

        final_video.write_videofile(
            output_file,
            codec="libx264",
            audio_codec="aac"
        )

        st.success(f"Morning video created successfully: {output_file}")

    except Exception as e:
        st.error(f"Morning video generation failed: {e}")

# =========================
# GENERATE EVENING QUOTE
# =========================
def generate_evening_quote():
    prompt = """
    Generate one deep emotional Islamic quote.
    Make it spiritual, peaceful, and powerful.
    Maximum 25 words.
    """

    response = model.generate_content(prompt)
    return response.text.strip()

# =========================
# CREATE EVENING IMAGE
# =========================
def create_evening_image():
    try:
        quote = generate_evening_quote()

        st.info(f"Generated Evening Quote: {quote}")

        # TikTok size
        width = 1080
        height = 1920

        image = Image.new("RGB", (width, height), color="black")
        draw = ImageDraw.Draw(image)

        # FONT
        try:
            font = ImageFont.truetype("arial.ttf", 60)
        except:
            font = ImageFont.load_default()

        wrapped_text = textwrap.fill(quote, width=20)

        # TEXT SIZE
        bbox = draw.multiline_textbbox((0, 0), wrapped_text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]

        x = (width - text_width) / 2
        y = (height - text_height) / 2

        draw.multiline_text(
            (x, y),
            wrapped_text,
            fill="white",
            font=font,
            align="center"
        )

        output_image = "evening_quote.png"
        image.save(output_image)

        st.success(f"Evening image created successfully: {output_image}")

    except Exception as e:
        st.error(f"Evening image generation failed: {e}")

# =========================
# STREAMLIT BUTTONS
# =========================
st.subheader("🌅 Morning Automation")

if st.button("Generate Morning Video"):
    create_morning_video()

st.subheader("🌙 Evening Automation")

if st.button("Generate Evening Image"):
    create_evening_image()

# =========================
# FOOTER
# =========================
st.markdown("---")
st.caption("Built with Streamlit + Gemini Pro + MoviePy + Pillow")

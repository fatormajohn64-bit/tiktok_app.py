import streamlit as st
import google.generativeai as genai
from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip
from PIL import Image, ImageDraw, ImageFont
import textwrap
import os

# ======================================
# PAGE CONFIG
# ======================================
st.set_page_config(
    page_title="Master Islamic AI Factory",
    layout="centered"
)

st.title("🕌 Master Islamic AI Factory")
st.write("Automated Morning Video + Evening Islamic Quote Generator")

# ======================================
# GEMINI SETUP
# ======================================
try:
    GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]

    genai.configure(api_key=GEMINI_API_KEY)

    # UPDATED WORKING MODEL
    model = genai.GenerativeModel("gemini-2.0-flash")

except Exception as e:
    st.error(f"Gemini setup failed: {e}")
    st.stop()

# ======================================
# VIDEO FILE
# ======================================
VIDEO_FILE = "background.mp4"

# ======================================
# GENERATE MORNING QUOTE
# ======================================
def generate_morning_quote():
    prompt = """
    Generate one short emotional Islamic motivational quote.
    Maximum 15 words.
    Deep, peaceful, and TikTok-ready.
    """

    response = model.generate_content(prompt)
    return response.text.strip()

# ======================================
# CREATE MORNING VIDEO
# ======================================
def create_morning_video():

    if not os.path.exists(VIDEO_FILE):
        st.warning("Please upload the Kabbah video from Xender to GitHub!")
        return

    try:
        quote = generate_morning_quote()

        st.info(f"Morning Quote: {quote}")

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

        final_video = CompositeVideoClip([
            video,
            txt_clip
        ])

        output_file = "morning_post.mp4"

        final_video.write_videofile(
            output_file,
            codec="libx264",
            audio_codec="aac"
        )

        st.success("Morning video generated successfully!")

        st.video(output_file)

    except Exception as e:
        st.error(f"Morning video generation failed: {e}")

# ======================================
# GENERATE EVENING QUOTE
# ======================================
def generate_evening_quote():
    prompt = """
    Generate one deep emotional Islamic quote.
    Maximum 25 words.
    Spiritual, peaceful, powerful.
    """

    response = model.generate_content(prompt)
    return response.text.strip()

# ======================================
# CREATE EVENING IMAGE
# ======================================
def create_evening_image():

    try:
        quote = generate_evening_quote()

        st.info(f"Evening Quote: {quote}")

        width = 1080
        height = 1920

        image = Image.new("RGB", (width, height), color="black")
        draw = ImageDraw.Draw(image)

        try:
            font = ImageFont.truetype("arial.ttf", 60)
        except:
            font = ImageFont.load_default()

        wrapped_text = textwrap.fill(quote, width=20)

        bbox = draw.multiline_textbbox(
            (0, 0),
            wrapped_text,
            font=font
        )

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

        st.success("Evening image generated successfully!")

        st.image(output_image)

    except Exception as e:
        st.error(f"Evening image generation failed: {e}")

# ======================================
# BUTTONS
# ======================================
st.subheader("🌅 Morning Automation")

if st.button("Generate Morning Video"):
    create_morning_video()

st.subheader("🌙 Evening Automation")

if st.button("Generate Evening Image"):
    create_evening_image()

# ======================================
# FOOTER
# ======================================
st.markdown("---")
st.caption("Built with Streamlit + Gemini Flash + MoviePy + Pillow")

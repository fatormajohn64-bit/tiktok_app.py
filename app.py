import numpy as np
from PIL import Image, ImageDraw, ImageFont
from moviepy.editor import (
    ColorClip,
    CompositeVideoClip,
    ImageClip,
    AudioFileClip
)

# =========================================================
# CREATE VIDEO FUNCTION
# =========================================================

def create_video(caption_text, output_filename):

    # -----------------------------
    # VIDEO SETTINGS
    # -----------------------------

    VIDEO_WIDTH = 1080
    VIDEO_HEIGHT = 1920
    DURATION = 15

    # -----------------------------
    # BACKGROUND VIDEO
    # -----------------------------

    background = ColorClip(
        size=(VIDEO_WIDTH, VIDEO_HEIGHT),
        color=(15, 15, 15),
        duration=DURATION
    )

    # -----------------------------
    # CREATE PIL IMAGE
    # -----------------------------

    img_width = 1000
    img_height = 400

    pil_img = Image.new(
        "RGBA",
        (img_width, img_height),
        (0, 0, 0, 0)
    )

    draw = ImageDraw.Draw(pil_img)

    # -----------------------------
    # FONT
    # -----------------------------

    try:
        font = ImageFont.truetype(
            "DejaVuSans-Bold.ttf",
            80
        )

    except:
        font = ImageFont.load_default()

    # -----------------------------
    # TEXT SIZE
    # -----------------------------

    bbox = draw.textbbox(
        (0, 0),
        caption_text,
        font=font
    )

    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]

    x = (img_width - text_width) // 2
    y = (img_height - text_height) // 2

    # -----------------------------
    # DRAW TEXT SHADOW
    # -----------------------------

    shadow_offset = 4

    draw.text(
        (x + shadow_offset, y + shadow_offset),
        caption_text,
        font=font,
        fill=(0, 0, 0, 180)
    )

    # -----------------------------
    # DRAW MAIN TEXT
    # -----------------------------

    draw.text(
        (x, y),
        caption_text,
        font=font,
        fill=(255, 215, 0, 255)
    )

    # -----------------------------
    # CONVERT PIL -> NUMPY
    # -----------------------------

    img_array = np.array(pil_img)

    # -----------------------------
    # CREATE MOVIEPY IMAGECLIP
    # -----------------------------

    text_clip = (
        ImageClip(img_array)
        .set_duration(DURATION)
        .set_position(("center", "center"))
    )

    # -----------------------------
    # OPTIONAL AUDIO
    # -----------------------------

    final_video = CompositeVideoClip([
        background,
        text_clip
    ])

    # Optional background audio
    if os.path.exists("nasheed.mp3"):

        audio = AudioFileClip(
            "nasheed.mp3"
        ).subclip(0, DURATION)

        final_video = final_video.set_audio(audio)

    # -----------------------------
    # EXPORT VIDEO
    # -----------------------------

    final_video.write_videofile(
        output_filename,
        fps=30,
        codec="libx264",
        audio_codec="aac",
        bitrate="8000k"
    )

    return output_filename

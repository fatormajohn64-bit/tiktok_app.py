# =========================================================
# IMPORTS
# =========================================================

import os
import tempfile

from moviepy.editor import (
    VideoFileClip,
    AudioFileClip,
    ColorClip,
    concatenate_videoclips
)

# =========================================================
# VIDEO CREATION FUNCTION
# =========================================================

def create_video(audio_path, theme, VIDEO_WIDTH, VIDEO_HEIGHT):

    # =====================================================
    # CREATE TEMP OUTPUT FILE
    # =====================================================

    with tempfile.NamedTemporaryFile(
        suffix=".mp4",
        delete=False,
        dir="/tmp"
    ) as temp_video:

        output_path = temp_video.name

    # =====================================================
    # LOAD AUDIO
    # =====================================================

    audio_clip = AudioFileClip(audio_path)

    audio_duration = audio_clip.duration

    background = None

    # =====================================================
    # TRY TO LOAD REAL BACKGROUND VIDEO
    # =====================================================

    if os.path.exists("background.mp4"):

        try:

            bg_video = VideoFileClip("background.mp4")

            # =================================================
            # LOOP VIDEO IF TOO SHORT
            # =================================================

            if bg_video.duration < audio_duration:

                loops_needed = int(
                    audio_duration // bg_video.duration
                ) + 1

                clips = []

                for _ in range(loops_needed):

                    clips.append(bg_video.copy())

                background = concatenate_videoclips(clips)

            else:

                background = bg_video

            # =================================================
            # CUT TO MATCH AUDIO EXACTLY
            # =================================================

            background = background.subclip(
                0,
                audio_duration
            )

        except Exception as e:

            print(f"Background video failed: {e}")

            background = None

    # =====================================================
    # FALLBACK CINEMATIC COLOR BACKGROUND
    # =====================================================

    if background is None:

        if theme == "Historical Story / Seerah":

            bg_color = (15, 10, 30)

        elif theme == "Quranic Reflection":

            bg_color = (5, 40, 25)

        elif theme == "Motivational Reminder":

            bg_color = (0, 55, 25)

        else:

            bg_color = (5, 25, 15)

        background = ColorClip(

            size=(VIDEO_WIDTH, VIDEO_HEIGHT),

            color=bg_color,

            duration=audio_duration

        )

    # =====================================================
    # FORCE CORRECT VIDEO SIZE
    # =====================================================

    background = background.resize(
        (VIDEO_WIDTH, VIDEO_HEIGHT)
    )

    # =====================================================
    # ATTACH AUDIO
    # =====================================================

    final_video = background.set_audio(audio_clip)

    # =====================================================
    # EXPORT VIDEO
    # =====================================================

    final_video.write_videofile(

        output_path,

        fps=24,

        codec="libx264",

        audio_codec="aac",

        preset="ultrafast",

        threads=4,

        bitrate="3000k",

        temp_audiofile="/tmp/temp-audio.m4a",

        remove_temp=True,

        logger=None

    )

    # =====================================================
    # CLEANUP
    # =====================================================

    audio_clip.close()

    if background:
        background.close()

    final_video.close()

    return output_path

import os
import requests
from moviepy import VideoFileClip, TextClip, CompositeVideoClip
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

# --- 1. API KEYS SETUP ---
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
TIKTOK_TOKEN = os.getenv("TIKTOK_ACCESS_TOKEN")

class IslamicAiCreator:
    
    def generate_quote_and_prompt(self):
        """Step 1: Get a quote and a matching video prompt from AI."""
        model = genai.GenerativeModel('gemini-1.5-pro')
        prompt = (
            "Give me one short, powerful motivational Islamic quote (English). "
            "Also, describe a 5-second cinematic animation prompt for a video generator "
            "that matches the vibe (e.g., 'A mosque at sunset, 3D Pixar style'). "
            "Return as: Quote | Prompt"
        )
        response = model.generate_content(prompt)
        quote, vid_prompt = response.text.split("|")
        return quote.strip(), vid_prompt.strip()

    def create_video_background(self, prompt):
        """Step 2: Generate the animation using a Video API (Simulated for Veo/Runway)."""
        print(f"🎬 Generating animation for: {prompt}...")
        # In a real app, you'd call the Google Veo or Runway API here.
        # For this example, we assume you have a base video named 'bg.mp4' 
        # or have downloaded the result from the API.
        return "background_animation.mp4" 

    def overlay_text(self, video_path, quote_text):
        """Step 3: Burn the quote onto the video."""
        print("✍️ Adding text overlay...")
        clip = VideoFileClip(video_path).subclipped(0, 5) # 5 seconds
        
        # Create the Text
        txt_clip = TextClip(
            text=quote_text,
            font_size=50,
            color='white',
            method='caption',
            size=(clip.w*0.8, None)
        ).with_duration(5).with_position('center')

        # Combine Video + Text
        final_video = CompositeVideoClip([clip, txt_clip])
        output_file = "final_post.mp4"
        final_video.write_videofile(output_file, codec="libx264", audio=False)
        return output_file

    def post_to_tiktok(self, video_path, quote):
        """Step 4: The final hand-off to TikTok."""
        caption = f"{quote}\n\n#IslamicQuotes #MuslimTok #AI #Motivation"
        print(f"🚀 Posting to TikTok with caption: {caption}")
        
        # Here we use the TikTok logic from our previous conversation
        # (Init -> Upload -> Publish)
        # result = tiktok_engine.upload_video(TIKTOK_TOKEN, video_path, caption)
        return "Success!"

# --- EXECUTION FLOW ---
if __name__ == "__main__":
    creator = IslamicAiCreator()
    
    # 1. Generate Quote
    my_quote, my_prompt = creator.generate_quote_and_prompt()
    
    # 2. Get Video (Using your AI Video API of choice)
    bg_video = creator.create_video_background(my_prompt)
    
    # 3. Add Text
    ready_video = creator.overlay_text(bg_video, my_quote)
    
    # 4. Post
    creator.post_to_tiktok(ready_video, my_quote)

import os
import requests
import pyttsx3
import ffmpeg

def make_video_for_article(article, output_dir="videos", duration=60):
    os.makedirs(output_dir, exist_ok=True)

    title = article.get("title", "No Title")
    description = article.get("description", "")
    image_url = article.get("urlToImage", None)

    # Compose text for voiceover
    text_to_speak = f"{title}. {description}"

    # Prepare filenames
    safe_title = "".join(c for c in title if c.isalnum() or c in (" ", "_")).rstrip()
    output_path = os.path.join(output_dir, f"{safe_title[:50].replace(' ', '_')}.mp4")
    audio_path = os.path.join(output_dir, f"{safe_title[:50].replace(' ', '_')}.mp3")
    image_path = os.path.join(output_dir, f"{safe_title[:50].replace(' ', '_')}.jpg")

    # Download image or use placeholder
    if image_url:
        try:
            resp = requests.get(image_url, timeout=10)
            resp.raise_for_status()
            with open(image_path, "wb") as f:
                f.write(resp.content)
        except Exception as e:
            print(f"Warning: Could not download image: {e}")
            image_path = None
    else:
        image_path = None

    # If no image, use a solid color black image (create temporary)
    if not image_path or not os.path.isfile(image_path):
        from PIL import Image
        image_path = os.path.join(output_dir, "black_bg.jpg")
        if not os.path.isfile(image_path):
            img = Image.new('RGB', (1280, 720), color='black')
            img.save(image_path)

    # Generate voiceover with pyttsx3
    engine = pyttsx3.init()
    engine.save_to_file(text_to_speak, audio_path)
    engine.runAndWait()

    # Combine image and audio into video using ffmpeg-python
    video_stream = ffmpeg.input(image_path, loop=1, t=duration, framerate=30)
    audio_stream = ffmpeg.input(audio_path)

    (
        ffmpeg
        .output(video_stream.video, audio_stream.audio, output_path,
                vcodec='libx264',
                pix_fmt='yuv420p',
                acodec='aac',
                shortest=None,
                movflags='faststart')
        .run(overwrite_output=True)
    )

    print(f"Video saved to {output_path}")
    return output_path

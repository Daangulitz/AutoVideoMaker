import cv2
import numpy as np
import os
from gtts import gTTS
from PIL import Image
import requests
from io import BytesIO
from pathlib import Path

def download_images(image_urls, save_dir):
    os.makedirs(save_dir, exist_ok=True)
    paths = []
    for i, url in enumerate(image_urls):
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            img = Image.open(BytesIO(response.content)).convert("RGB")
            file_path = os.path.join(save_dir, f"image_{i}.jpg")
            img.save(file_path)
            paths.append(file_path)
        except Exception as e:
            print(f"❌ Error downloading image {i}: {e}")
    return paths

def generate_narration(text, output_path):
    tts = gTTS(text)
    tts.save(output_path)

def create_video(image_paths, audio_path, output_path, duration_per_image=6):
    if not image_paths:
        print("❌ No images to create video.")
        return

    frame_width = 1280
    frame_height = 720
    fps = 1  # 1 frame per second

    # VideoWriter
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    video_writer = cv2.VideoWriter(output_path, fourcc, fps, (frame_width, frame_height))

    for image_path in image_paths:
        img = Image.open(image_path)
        img = img.resize((frame_width, frame_height))
        frame = np.array(img)
        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

        for _ in range(duration_per_image):
            video_writer.write(frame)

    video_writer.release()

    # Add audio using ffmpeg-python fallback
    try:
        import ffmpeg
        temp = output_path.replace(".mp4", "_with_audio.mp4")
        ffmpeg.input(output_path).output(audio_path, temp, vcodec='copy', acodec='aac', strict='experimental').run(overwrite_output=True)
        os.replace(temp, output_path)
    except Exception as e:
        print("⚠️ Could not add audio:", e)

def make_video(article, image_urls, output_dir="outputs"):
    title = article.get("title", "No Title")
    description = article.get("description", "No Description")
    text = f"{title}. {description}"

    Path(output_dir).mkdir(parents=True, exist_ok=True)
    basename = title[:30].replace(" ", "_").replace("/", "")  # Safe filename
    audio_path = os.path.join(output_dir, f"{basename}_audio.mp3")
    video_path = os.path.join(output_dir, f"{basename}.mp4")
    image_dir = os.path.join(output_dir, basename)

    generate_narration(text, audio_path)
    image_paths = download_images(image_urls, image_dir)
    create_video(image_paths, audio_path, video_path)

    return video_path

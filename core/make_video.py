import cv2
import numpy as np
import requests
from io import BytesIO
from PIL import Image
import pyttsx3
import tempfile
import os

from core.pexels_image_search import search_pexels_images, search_pexels_videos

def download_image(url):
    resp = requests.get(url)
    resp.raise_for_status()
    image = Image.open(BytesIO(resp.content)).convert("RGB")
    return np.array(image)

def download_video(url, output_path):
    # Download the video file to output_path
    resp = requests.get(url, stream=True)
    resp.raise_for_status()
    with open(output_path, "wb") as f:
        for chunk in resp.iter_content(chunk_size=8192):
            f.write(chunk)

def make_video_for_article(article, pexels_api_key, duration_sec=60, output_path="output.mp4"):
    title = article.get("title", "No Title")
    description = article.get("description", "No description available.")
    query = title or "news"

    print(f"Searching images and videos for: {query}")
    image_urls = search_pexels_images(query, pexels_api_key, count=3)
    video_urls = search_pexels_videos(query, pexels_api_key, count=2)

    # Download and prepare media
    images = []
    for url in image_urls:
        try:
            img = download_image(url)
            img = cv2.resize(img, (1280, 720))
            images.append(img)
        except Exception as e:
            print(f"Failed to download image: {url} error: {e}")

    temp_video_files = []
    for idx, vurl in enumerate(video_urls):
        temp_path = f"temp_video_{idx}.mp4"
        try:
            print(f"Downloading video {vurl}")
            download_video(vurl, temp_path)
            temp_video_files.append(temp_path)
        except Exception as e:
            print(f"Failed to download video: {vurl} error: {e}")

    # Setup TTS engine and save narration audio (optional)
    tts = pyttsx3.init()
    tts.setProperty('rate', 150)
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_audio:
        tts.save_to_file(description, tmp_audio.name)
        tts.runAndWait()
        audio_path = tmp_audio.name
    print(f"Narration audio saved at: {audio_path}")

    # Setup OpenCV VideoWriter
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    fps = 30
    out = cv2.VideoWriter(output_path, fourcc, fps, (1280, 720))

    total_frames = duration_sec * fps
    title_duration_frames = fps * 5  # 5 seconds showing title text

    # 1) Show title text on black background for first 5 seconds
    black_frame = np.zeros((720, 1280, 3), dtype=np.uint8)
    for i in range(title_duration_frames):
        frame = black_frame.copy()
        cv2.putText(frame, title, (50, 100), cv2.FONT_HERSHEY_SIMPLEX,
                    1.5, (255, 255, 255), 3, cv2.LINE_AA)
        out.write(frame)

    # 2) Calculate frames left after title
    frames_left = total_frames - title_duration_frames

    # 3) Compose slideshow with images and videos:
    # Strategy:
    # - Each image shows for 3 seconds
    # - Each video plays for up to 5 seconds
    # - Alternate images and videos, loop if necessary

    image_frame_count = 3 * fps
    video_frame_count = 5 * fps

    idx_img, idx_vid = 0, 0
    current_frame = 0

    # Preload videos into cv2.VideoCapture
    video_caps = []
    for vfile in temp_video_files:
        cap = cv2.VideoCapture(vfile)
        video_caps.append(cap)

    while current_frame < frames_left:
        # Show image for 3 sec
        if images:
            img = images[idx_img % len(images)]
            for _ in range(image_frame_count):
                if current_frame >= frames_left:
                    break
                out.write(img)
                current_frame += 1
            idx_img += 1

        # Show video for 5 sec
        if video_caps:
            cap = video_caps[idx_vid % len(video_caps)]
            frames_read = 0
            while frames_read < video_frame_count and current_frame < frames_left:
                ret, frame = cap.read()
                if not ret:
                    cap.set(cv2.CAP_PROP_POS_FRAMES, 0)  # Loop video
                    ret, frame = cap.read()
                    if not ret:
                        break
                frame = cv2.resize(frame, (1280, 720))
                out.write(frame)
                current_frame += 1
                frames_read += 1
            idx_vid += 1

    # Release video captures and writer
    for cap in video_caps:
        cap.release()
    out.release()

    # Clean up temp video files
    for vfile in temp_video_files:
        if os.path.exists(vfile):
            os.remove(vfile)

    print(f"Video saved to {output_path}")
    print("NOTE: Narration audio saved separately; combine with video externally if needed.")

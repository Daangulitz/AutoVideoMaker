import os
import requests
from io import BytesIO
from PIL import Image
from gtts import gTTS
import ffmpeg

def download_images(image_urls, folder="images"):
    os.makedirs(folder, exist_ok=True)
    paths = []
    for i, url in enumerate(image_urls):
        try:
            r = requests.get(url, timeout=10)
            r.raise_for_status()
            img = Image.open(BytesIO(r.content)).convert("RGB")
            path = os.path.join(folder, f"img_{i:03d}.jpg")
            img.save(path)
            paths.append(path)
        except Exception as e:
            print(f"Failed to download image {url}: {e}")
    return paths

def generate_audio(text, filename="audio.mp3"):
    tts = gTTS(text)
    tts.save(filename)
    return filename

def create_video_from_images(image_files, output_file, image_duration=5, fps=24):
    # Create a text file listing images for ffmpeg concat demuxer
    list_file = "images.txt"
    with open(list_file, "w") as f:
        for img_path in image_files:
            f.write(f"file '{os.path.abspath(img_path)}'\n")
            f.write(f"duration {image_duration}\n")
        # To ensure last image duration is used (ffmpeg quirk)
        f.write(f"file '{os.path.abspath(image_files[-1])}'\n")

    # Build video from images using ffmpeg concat demuxer
    # Note: Must use -safe 0 for absolute paths
    ffmpeg_cmd = (
        ffmpeg
        .input(list_file, format='concat', safe=0)
        .output(output_file, vcodec='libx264', pix_fmt='yuv420p', r=fps)
        .overwrite_output()
    )
    ffmpeg_cmd.run()
    os.remove(list_file)
    return output_file

def combine_audio_video(video_file, audio_file, output_file):
    input_video = ffmpeg.input(video_file)
    input_audio = ffmpeg.input(audio_file)
    ffmpeg.output(input_video.video, input_audio.audio, output_file, vcodec='copy', acodec='aac', strict='experimental').overwrite_output().run()
    return output_file

if __name__ == "__main__":
    article_title = "Amazing Nature Photos"
    article_description = "A collection of breathtaking views from around the world."
    text = f"{article_title}. {article_description}"

    images = [
        "https://images.unsplash.com/photo-1506744038136-46273834b3fb?auto=format&fit=crop&w=800&q=80",
        "https://images.unsplash.com/photo-1500534623283-312aade485b7?auto=format&fit=crop&w=800&q=80",
        "https://images.unsplash.com/photo-1470770841072-f978cf4d019e?auto=format&fit=crop&w=800&q=80",
    ]

    print("Downloading images...")
    image_files = download_images(images)

    print("Generating audio...")
    audio_file = generate_audio(text)

    temp_video = "temp_video.mp4"
    output_video = "final_video_with_audio.mp4"

    print("Creating video from images...")
    create_video_from_images(image_files, temp_video, image_duration=5)

    print("Combining video and audio...")
    combine_audio_video(temp_video, audio_file, output_video)

    print(f"Video created: {output_video}")

    # Cleanup temp video if you want
    os.remove(temp_video)

from moviepy.editor import TextClip, CompositeVideoClip, concatenate_videoclips, ColorClip
import math
import os

def make_video(script_text, output_path="output/video.mp4", duration=60, fps=24):

    os.makedirs(os.path.irname(output_path), exist_ok=True)

    n_parts = 4
    script_length = len(script_text)
    chunk_size = math.ceil(script_length / n_parts)
    chunks = [script.text[i:i + chunk_size] for i in range]
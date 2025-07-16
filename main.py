import os
from core.fetch_news import fetch_news
from core.generate_script import generate_script  
from core.make_video import make_video_for_article

def main():
    pexels_api_key = "a6BNeU50yI8V5dTVJoUanxt6WqME3XOp4AQe7asZdvX0wCXWr0nNrtqX"  
    articles = fetch_news(country="us", page_size=3)
    output_dir = "output_videos"
    os.makedirs(output_dir, exist_ok=True)

    for idx, article in enumerate(articles):
        output_path = os.path.join(output_dir, f"article_{idx+1}.mp4")
        print(f"Creating video for article {idx+1}: {article.get('title')}")
        make_video_for_article(article, pexels_api_key, duration_sec=60, output_path=output_path)

if __name__ == "__main__":
    main()

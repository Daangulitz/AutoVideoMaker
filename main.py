# main.py

import os
from core.generate_script import generate_script
from core.fetch_news import fetch_news
from core.image_fetcher import fetch_image_urls
from core.make_video import make_video

# Config constants (adjust if needed)
OUTPUT_DIR = "outputs"
NEWS_API_PAGE_SIZE = 3
GOOGLE_API_KEY = 'AIzaSyChJ3ygRo98LslFDxm7OopoBqqlPfx9y_g'
GOOGLE_CX = 'f54d4c38836df40ac'
NUM_IMAGES_PER_ARTICLE = 5

def main():
    articles = fetch_news(page_size=NEWS_API_PAGE_SIZE)
    if not articles:
        print("❌ No articles fetched. Exiting.")
        return

    for idx, article in enumerate(articles, 1):
        title = article.get("title", "No Title")
        print(f"\n[{idx}] Processing article: {title}")

        try:
            # Generate narration script from article content
            script_text = generate_script(article)
            print(f"✍️ Script generated (preview): {script_text[:80]}...")

            # Fetch images for this article's title
            image_urls = fetch_image_urls(title, GOOGLE_API_KEY, GOOGLE_CX, NUM_IMAGES_PER_ARTICLE)
            if not image_urls:
                print("❌ No images found, skipping video.")
                continue

            # Make TikTok-style video
            video_path = make_video(article, image_urls, OUTPUT_DIR)
            print(f"✅ Video created: {video_path}")

        except Exception as e:
            print(f"❌ Error processing '{title}': {e}")

if __name__ == "__main__":
    main()

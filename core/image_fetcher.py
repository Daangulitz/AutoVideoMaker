import os
import re
import requests
from googleapiclient.discovery import build

# ========== CONFIGURATION ==========
API_KEY = 'AIzaSyChJ3ygRo98LslFDxm7OopoBqqlPfx9y_g'
CX = 'f54d4c38836df40ac'
NUM_IMAGES = 10
OUTPUT_DIR = 'outputs'
# ===================================

def sanitize_filename(name):
    """Remove invalid characters from filenames and folder names."""
    return re.sub(r'[<>:"/\\|?*\']', '', name)

def fetch_image_urls(query, api_key, cx, num_images=10):
    """Use Google Custom Search API to fetch image URLs for a query."""
    service = build("customsearch", "v1", developerKey=api_key)
    res = service.cse().list(
        q=query,
        cx=cx,
        searchType='image',
        num=num_images,
    ).execute()

    image_urls = [item['link'] for item in res.get('items', [])]
    print(f"✅ Found {len(image_urls)} images for '{query}'")
    return image_urls

def download_images(image_urls, save_dir):
    """Download images to the specified folder."""
    os.makedirs(save_dir, exist_ok=True)
    saved_paths = []

    for index, url in enumerate(image_urls):
        try:
            if not url.startswith("http"):
                print(f"❌ Skipping invalid URL: {url}")
                continue

            response = requests.get(url, timeout=10)
            response.raise_for_status()

            file_path = os.path.join(save_dir, f"image_{index}.jpg")
            with open(file_path, "wb") as f:
                f.write(response.content)

            saved_paths.append(file_path)

        except Exception as e:
            print(f"❌ Error downloading image {index}: {e}")

    return saved_paths

def process_articles(articles):
    for i, title in enumerate(articles, 1):
        print(f"[{i}] Processing article: {title}")
        safe_title = sanitize_filename(title)
        article_dir = os.path.join(OUTPUT_DIR, safe_title)

        try:
            image_urls = fetch_image_urls(title, API_KEY, CX, NUM_IMAGES)
            downloaded = download_images(image_urls, article_dir)

            if not downloaded:
                print(f"❌ No images downloaded for '{title}'")
                continue

            print(f"🎬 Images saved for article '{title}' in {article_dir}")

            # 🔧 Add your video generation logic here if needed

        except Exception as e:
            print(f"❌ Error processing '{title}': {e}")

if __name__ == "__main__":
    # Example article titles
    article_titles = [
        "Former H&M CEO Helena Helmersson Joins Mango Board",
        "Animal populations threatened by Arctic sea ice melt",
        "University of Michigan faces federal investigation after arrest of 2 Chinese scientists",
        "Drummer Matt Cameron hasn’t retired despite leaving Pearl Jam"
    ]

    process_articles(article_titles)

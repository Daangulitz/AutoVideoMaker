from core.make_card import make_image_card
from core.fetch_news import fetch_news
from core.image_fetcher import fetch_image_urls
import os

PROCESSED_FILE = "processed.txt"

def load_processed():
    if not os.path.exists(PROCESSED_FILE):
        return set()
    with open(PROCESSED_FILE, "r", encoding="utf-8") as f:
        return set(line.strip() for line in f.readlines())

def save_processed(title):
    with open(PROCESSED_FILE, "a", encoding="utf-8") as f:
        f.write(title + "\n")

def main():
    API_KEY = "AIzaSyChJ3ygRo98LslFDxm7OopoBqqlPfx9y_g"
    CX = "f54d4c38836df40ac"
    
    processed_titles = load_processed()
    articles = fetch_news(page_size=100)  

    for article in articles:
        title = article["title"].strip()
        if title in processed_titles:
            print(f"⏭ Skipping already processed article: {title}")
            continue

        try:
            print(f"[+] Processing article: {title}")

            image_urls = fetch_image_urls(title, API_KEY, CX, num_images=1)
            if not image_urls:
                print("❌ No image found.")
                continue

            image_url = image_urls[0]
            make_image_card(image_url, title, output_path=f"output_{len(processed_titles)+1}.jpg")

            save_processed(title)
            break

        except Exception as e:
            print(f"❌ Error creating image card: {e}")

if __name__ == "__main__":
    main()

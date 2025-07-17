from core.fetch_news import fetch_news
from core.generate_script import generate_script
from core.image_fetcher import fetch_image_urls
from core.make_video import make_video

# Your API config here
API_KEY = 'YOUR_API_KEY'
CX = 'YOUR_CX_CODE'

def main():
    articles = fetch_news(page_size=3)

    for article in articles:
        try:
            print(f"[+] Processing article: {article['title']}")
            
            # Generate narration script/text for video
            script_text = generate_script(article)
            
            # Fetch image URLs based on article title
            image_urls = fetch_image_urls(article["title"], API_KEY, CX, num_images=10)
            
            # Make video with the article info and images
            video_path = make_video(article, image_urls, narration_text=script_text)
            
            if video_path:
                print(f"✅ Video created: {video_path}")
            else:
                print(f"⚠️ Skipped video for article: {article['title']}")
        except Exception as e:
            print(f"❌ Error processing '{article['title']}': {e}")

if __name__ == "__main__":
    main()

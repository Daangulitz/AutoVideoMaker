from core.fetch_news import fetch_news
from core.make_video import make_video_for_article

def main():
    articles = fetch_news()  # this returns a list of dicts

    for article in articles:
        make_video_for_article(article=article, duration=60)

if __name__ == "__main__":
    main()

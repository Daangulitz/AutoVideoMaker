import os
import requests
from core.settings import NEWS_API_KEY, ARTICLE_COUNT

BASE_URL = "https://newsapi.org/v2/top-headlines"

# Global sources (you can add more if needed)
GLOBAL_SOURCES = "bbc-news,cnn,al-jazeera-english,reuters,associated-press"

def fetch_top_headlines():
    params = {
        "sources": GLOBAL_SOURCES,
        "pageSize": ARTICLE_COUNT,
        "apiKey": NEWS_API_KEY
    }

    try:
        response = requests.get(BASE_URL, params=params)
        response.raise_for_status()
        data = response.json()
        articles = data.get("articles", [])
        
        if not articles:
            print("⚠️ No articles found.")
            return []

        # Simplify article structure
        simplified = [
            {
                "title": article["title"],
                "description": article["description"],
                "url": article["url"],
                "content": article.get("content", ""),
                "source": article["source"]["name"]
            }
            for article in articles
        ]

        return simplified

    except requests.exceptions.RequestException as e:
        print(f"❌ Error fetching news: {e}")
        return []

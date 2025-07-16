import requests

def fetch_news(page_size=3):
    api_key = "70fd13c91ea049449019a2dbd5a85d56"

    url = "https://newsapi.org/v2/everything"
    params = {
        "apiKey": api_key,
        "q": "breaking OR world OR international", 
        "language": "en",
        "sortBy": "publishedAt",
        "pageSize": page_size
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        return data.get("articles", [])
    except Exception as e:
        print(f"❌ Error fetching news: {e}")
        return []

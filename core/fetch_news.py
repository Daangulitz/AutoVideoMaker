import requests

def fetch_news(page_size=3):
    api_key = "70fd13c91ea049449019a2dbd5a85d56"

    url = "https://newsapi.org/v2/top-headlines"
    params = {
        "apiKey": api_key,
        "language": "en",
        "pageSize": page_size,
        "category": "general",  # You can also try 'world' or 'business' etc.
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        return data.get("articles", [])
    except Exception as e:
        print(f"❌ Error fetching news: {e}")
        return []

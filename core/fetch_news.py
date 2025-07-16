# core/fetch_news.py
import requests

def fetch_news(country=None, page_size=5):
    api_key = "70fd13c91ea049449019a2dbd5a85d56"
    
    if country:
        url = "https://newsapi.org/v2/top-headlines"
        params = {
            "apiKey": api_key,
            "pageSize": page_size,
            "country": country
        }
    else:
        url = "https://newsapi.org/v2/everything"
        params = {
            "apiKey": api_key,
            "pageSize": page_size,
            "q": "latest"
        }

    response = requests.get(url, params=params)
    response.raise_for_status()
    data = response.json()
    return data.get("articles", [])

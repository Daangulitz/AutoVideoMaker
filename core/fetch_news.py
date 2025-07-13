from dotenv import load_dotenv
load_dotenv()

import os
import requests
from dataclasses import dataclass
from typing import List, Optional


#
# Data Model
#

@dataclass
class Story:
    headline: str
    url: str
    image_url: Optional[str] = None


#
# News Fetching
#

def fetch_top_stories(api_key: str, *, country: str="us", limit: int = 5 ) -> List[Story]:
    url = "https://newsapi.org/v2/top-headlines"
    params = {
        "counntry" : country,
        "pageSize": limit,
        "apiKey": api_key,
    }
    response = requests.get(url, params=params, timeout=10)
    response.raise_for_status()

    articles = response.json().get("articles", [])
    stories = []

    for article in articles:
        if not article.get("title") or not article.get("url"):
            continue
        stories.append(
            Story(
                headline=article["title"].strip(),
                url=article["url"],
                image_url=article.get("urlToImage")
            )
        )
    return stories

#
# Run Demo
#

if __name__ == "__main__":
    API_KEY = os.getenv("NEWSAPI_KEY")
    if not API_KEY:
        raise EnvironmentError("Please set the NEWSAPI_KEY environment variable")
    
    stories = fetch_top_stories(API_KEY, country="us", limit=3)
    for i, s in enumerate(stories, 1):
        print(f"{i}. {s.headline}\n{s.url}\n")
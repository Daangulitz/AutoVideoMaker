import requests

def search_pexels_images(query, api_key, count=3):
    url = "https://api.pexels.com/v1/search"
    headers = {
        "Authorization": api_key
    }
    params = {
        "query": query,
        "per_page": count,
        "page": 1
    }
    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    data = response.json()
    image_urls = [photo["src"]["medium"] for photo in data.get("photos", [])]
    return image_urls

def search_pexels_videos(query, api_key, count=2):
    url = "https://api.pexels.com/videos/search"
    headers = {
        "Authorization": api_key
    }
    params = {
        "query": query,
        "per_page": count,
        "page": 1
    }
    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    data = response.json()
    video_urls = []
    for video in data.get("videos", []):
        # Get video file with medium resolution
        files = video.get("video_files", [])
        if files:
            # pick the first mp4 medium quality file
            mp4_files = [f for f in files if f["file_type"] == "video/mp4"]
            if mp4_files:
                # sort by width ascending to pick medium quality
                mp4_files.sort(key=lambda x: x["width"])
                video_urls.append(mp4_files[len(mp4_files)//2]["link"])
    return video_urls

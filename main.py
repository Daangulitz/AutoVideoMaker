import os
import requests
import webbrowser
import base64
import hashlib
from urllib.parse import urlparse, parse_qs

from requests_oauthlib import OAuth1Session

from core.make_card import make_image_card
from core.fetch_news import fetch_news
from core.image_fetcher import fetch_image_urls

# ====== CONFIG ======
CLIENT_ID = "b3d6WnJneDNmaU1FbmltS0FSV3M6MTpjaQ"
CLIENT_SECRET = "jpv_ZcPV_1eG-xSmiT778BjOOwBBnl2n7WIa-vzMMQHbYQzh6y"
REDIRECT_URI = "http://localhost:8000/callback"  # Just for matching registered URI

CONSUMER_KEY = "d52Ek0t5LhvzdF5pqVsYUDSiv"
CONSUMER_SECRET = "K1N0XuXhIJCCYvtrfMzQ8FOmie6qIYYNKP3GqZbkOuKmmsYV66"
ACCESS_TOKEN_1 = "1948437875785338880-x5Y7BZmQvnJI6jYGCntRuDGHC2XWqL"
ACCESS_TOKEN_SECRET = "zGDIRqQwiHdqRvpbHn03zOWtB0LkpMhifu3AF6Nkw2I6V"

GOOGLE_API_KEY = "AIzaSyChJ3ygRo98LslFDxm7OopoBqqlPfx9y_g"
CX = "f54d4c38836df40ac"

PROCESSED_FILE = "processed.txt"
SCOPES = ["tweet.read", "tweet.write", "users.read", "offline.access"]

AUTHORIZATION_BASE_URL = "https://twitter.com/i/oauth2/authorize"
TOKEN_URL = "https://api.twitter.com/2/oauth2/token"

# ====================


def generate_code_verifier():
    # PKCE code verifier: random 43-128 chars base64 URL-safe
    return base64.urlsafe_b64encode(os.urandom(40)).rstrip(b'=').decode('utf-8')


def generate_code_challenge(verifier):
    # PKCE S256 code challenge
    digest = hashlib.sha256(verifier.encode('utf-8')).digest()
    return base64.urlsafe_b64encode(digest).rstrip(b'=').decode('utf-8')


def get_auth_code(code_challenge):
    # Build auth URL
    params = {
        "response_type": "code",
        "client_id": CLIENT_ID,
        "redirect_uri": REDIRECT_URI,
        "scope": " ".join(SCOPES),
        "state": "state_example",
        "code_challenge": code_challenge,
        "code_challenge_method": "S256",
    }
    url_params = "&".join(f"{k}={requests.utils.quote(v)}" for k, v in params.items())
    auth_url = f"{AUTHORIZATION_BASE_URL}?{url_params}"

    print("[🔐] Go to this URL and authorize the app:\n")
    print(auth_url)
    print("\nAfter authorization, you will be redirected to a URL.")
    redirected_url = input("Paste the full redirected URL here:\n").strip()

    # Extract code from redirected URL
    parsed = urlparse(redirected_url)
    query = parse_qs(parsed.query)
    return query.get("code", [None])[0]


def get_token(auth_code, code_verifier):
    data = {
        "grant_type": "authorization_code",
        "code": auth_code,
        "redirect_uri": REDIRECT_URI,
        "client_id": CLIENT_ID,
        "code_verifier": code_verifier,
    }
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
    }
    response = requests.post(TOKEN_URL, data=data, headers=headers, auth=(CLIENT_ID, CLIENT_SECRET))
    response.raise_for_status()
    return response.json()


def upload_media_oauth1(image_path):
    oauth1 = OAuth1Session(
        client_key=CONSUMER_KEY,
        client_secret=CONSUMER_SECRET,
        resource_owner_key=ACCESS_TOKEN_1,
        resource_owner_secret=ACCESS_TOKEN_SECRET,
    )
    with open(image_path, "rb") as f:
        files = {"media": f}
        response = oauth1.post("https://upload.twitter.com/1.1/media/upload.json", files=files)
    response.raise_for_status()
    return response.json()["media_id_string"]


def post_tweet_oauth2(bearer_token, text, media_id=None):
    headers = {
        "Authorization": f"Bearer {bearer_token}",
        "Content-Type": "application/json",
    }
    payload = {"text": text}
    if media_id:
        payload["media"] = {"media_ids": [media_id]}
    response = requests.post("https://api.twitter.com/2/tweets", headers=headers, json=payload)
    response.raise_for_status()
    return response.json()


def load_processed():
    if not os.path.exists(PROCESSED_FILE):
        return set()
    with open(PROCESSED_FILE, "r", encoding="utf-8") as f:
        return set(line.strip() for line in f)


def save_processed(title):
    with open(PROCESSED_FILE, "a", encoding="utf-8") as f:
        f.write(title + "\n")


def main():
    processed_titles = load_processed()
    articles = fetch_news(page_size=25)

    print("[📰] Checking for new articles...")

    for article in articles:
        title = article["title"].strip()
        if title in processed_titles:
            print(f"⏩ Already posted: {title}")
            continue

        try:
            print(f"[+] Processing: {title}")

            image_urls = fetch_image_urls(title, GOOGLE_API_KEY, CX, num_images=1)
            if not image_urls:
                print("❌ No image found.")
                continue

            image_url = image_urls[0]
            image_path = f"output_{len(processed_titles) + 1}.png"

            make_image_card(image_url, title, output_path=image_path)

            print("[📤] Uploading media to Twitter...")
            media_id = upload_media_oauth1(image_path)

            print("[🔐] Starting OAuth2 flow for posting tweet...")

            # Generate PKCE verifier and challenge
            code_verifier = generate_code_verifier()
            code_challenge = generate_code_challenge(code_verifier)

            auth_code = get_auth_code(code_challenge)
            if not auth_code:
                print("❌ Authorization code not found.")
                return

            token_data = get_token(auth_code, code_verifier)
            bearer_token = token_data["access_token"]

            print("[🐦] Posting tweet...")
            tweet = post_tweet_oauth2(bearer_token, title, media_id)

            tweet_id = tweet["data"]["id"]
            print(f"✅ Tweet posted: https://twitter.com/i/web/status/{tweet_id}")

            save_processed(title)
            break  # Only post one article per run

        except Exception as e:
            print(f"❌ Error posting: {e}")
            break


if __name__ == "__main__":
    main()
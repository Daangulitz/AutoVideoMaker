import os
import json
import requests
import webbrowser
from urllib.parse import parse_qs, urlparse
from http.server import HTTPServer, BaseHTTPRequestHandler
from requests_oauthlib import OAuth2Session, OAuth1Session

# =========== CONFIGURE THESE ============
# OAuth 2.0 credentials
CLIENT_ID = "b3d6WnJneDNmaU1FbmltS0FSV3M6MTpjaQ"
CLIENT_SECRET = "jpv_ZcPV_1eG-xSmiT778BjOOwBBnl2n7WIa-vzMMQHbYQzh6y"
REDIRECT_URI = "http://localhost:8000/callback"

# OAuth 1.0a credentials (for media upload)
CONSUMER_KEY = "d52Ek0t5LhvzdF5pqVsYUDSiv"
CONSUMER_SECRET = "K1N0XuXhIJCCYvtrfMzQ8FOmie6qIYYNKP3GqZbkOuKmmsYV66"
ACCESS_TOKEN_1 = "1948437875785338880-x5Y7BZmQvnJI6jYGCntRuDGHC2XWqL"
ACCESS_TOKEN_SECRET = "zGDIRqQwiHdqRvpbHn03zOWtB0LkpMhifu3AF6Nkw2I6V"

# Tweet content
TWEET_TEXT = "Auto-posted from Python! 🚀"
IMAGE_PATH = "output.png"

# ========================================

AUTHORIZATION_BASE_URL = "https://twitter.com/i/oauth2/authorize"
TOKEN_URL = "https://api.twitter.com/2/oauth2/token"
SCOPES = ["tweet.read", "tweet.write", "users.read", "offline.access"]


# Handle OAuth2 redirect and extract authorization code
class OAuthCallbackHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        query = urlparse(self.path).query
        params = parse_qs(query)
        self.server.auth_code = params.get("code", [None])[0]
        self.send_response(200)
        self.send_header("Content-Type", "text/html")
        self.end_headers()
        self.wfile.write("✅ Authorization successful. You can close this window.".encode("utf-8"))


def get_auth_code():
    oauth = OAuth2Session(CLIENT_ID, redirect_uri=REDIRECT_URI, scope=SCOPES)
    auth_url, _ = oauth.authorization_url(
        AUTHORIZATION_BASE_URL,
        code_challenge_method='plain',
        code_challenge='challenge'
    )
    print("[!] Opening browser for authorization...")
    webbrowser.open(auth_url)
    httpd = HTTPServer(('localhost', 8000), OAuthCallbackHandler)
    httpd.handle_request()
    return httpd.auth_code


def get_token(auth_code):
    data = {
        "grant_type": "authorization_code",
        "code": auth_code,
        "redirect_uri": REDIRECT_URI,
        "client_id": CLIENT_ID,
        "code_verifier": "challenge"
    }
    response = requests.post(TOKEN_URL, data=data, auth=(CLIENT_ID, CLIENT_SECRET))
    response.raise_for_status()
    return response.json()


def upload_media_oauth1(image_path):
    print("[📤] Uploading image using OAuth1...")
    oauth1 = OAuth1Session(
        client_key=CONSUMER_KEY,
        client_secret=CONSUMER_SECRET,
        resource_owner_key=ACCESS_TOKEN_1,
        resource_owner_secret=ACCESS_TOKEN_SECRET
    )
    with open(image_path, "rb") as f:
        files = {"media": f}
        response = oauth1.post("https://upload.twitter.com/1.1/media/upload.json", files=files)
    response.raise_for_status()
    media_id = response.json()["media_id_string"]
    print("✅ Uploaded media:", media_id)
    return media_id


def post_tweet_oauth2(bearer_token, text, media_id=None):
    headers = {
        "Authorization": f"Bearer {bearer_token}",
        "Content-Type": "application/json"
    }
    payload = {"text": text}
    if media_id:
        payload["media"] = {"media_ids": [media_id]}
    response = requests.post("https://api.twitter.com/2/tweets", headers=headers, json=payload)
    response.raise_for_status()
    print("✅ Tweet posted:", response.json()["data"]["id"])


def main():
    print("[1] Getting authorization code...")
    auth_code = get_auth_code()

    print("[2] Exchanging code for token...")
    token_data = get_token(auth_code)
    access_token = token_data["access_token"]

    print("[3] Uploading image to Twitter...")
    media_id = upload_media_oauth1(IMAGE_PATH)

    print("[4] Posting tweet...")
    post_tweet_oauth2(access_token, TWEET_TEXT, media_id)


if __name__ == "__main__":
    main()

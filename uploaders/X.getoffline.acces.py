import base64
import hashlib
import os
import time
import webbrowser
from urllib.parse import urlencode, urlparse, parse_qs

import requests
from http.server import HTTPServer, BaseHTTPRequestHandler


# === YOUR TWITTER APP CONFIG ===
CLIENT_ID = 'b3d6WnJneDNmaU1FbmltS0FSV3M6MTpjaQ'
REDIRECT_URI = 'http://localhost:8080/callback'
SCOPES = 'tweet.write tweet.read users.read offline.access'


# === Helper: Generate PKCE code verifier + challenge ===
def generate_pkce():
    code_verifier = base64.urlsafe_b64encode(os.urandom(40)).rstrip(b'=').decode('utf-8')
    code_challenge = base64.urlsafe_b64encode(
        hashlib.sha256(code_verifier.encode('utf-8')).digest()
    ).rstrip(b'=').decode('utf-8')
    return code_verifier, code_challenge


# === Helper: Handle OAuth callback ===
class OAuthCallbackHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        query = parse_qs(urlparse(self.path).query)
        self.server.auth_code = query.get("code", [None])[0]
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b" You can close this window now.")


def start_http_server():
    server = HTTPServer(('localhost', 8080), OAuthCallbackHandler)
    server.handle_request()
    return server.auth_code


# === Step 1: Direct user to authorize ===
def get_authorization_code(client_id, redirect_uri, scopes):
    code_verifier, code_challenge = generate_pkce()
    auth_url = (
        f"https://twitter.com/i/oauth2/authorize?"
        + urlencode({
            'response_type': 'code',
            'client_id': client_id,
            'redirect_uri': redirect_uri,
            'scope': scopes,
            'state': 'state123',
            'code_challenge': code_challenge,
            'code_challenge_method': 'S256',
        })
    )

    print(f"[🌐] Opening browser for authorization...")
    webbrowser.open(auth_url)
    print(f"[🔁] Waiting for callback on {redirect_uri} ...")

    auth_code = start_http_server()
    return auth_code, code_verifier


# === Step 2: Exchange code for access & refresh tokens ===
def exchange_code_for_token(code, code_verifier):
    token_url = "https://api.twitter.com/2/oauth2/token"
    data = {
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': REDIRECT_URI,
        'client_id': CLIENT_ID,
        'code_verifier': code_verifier,
    }
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}

    response = requests.post(token_url, data=data, headers=headers)
    response.raise_for_status()
    return response.json()


# === Run it ===
def main():
    auth_code, verifier = get_authorization_code(CLIENT_ID, REDIRECT_URI, SCOPES)
    if not auth_code:
        print("❌ Failed to get auth code.")
        return

    print("[🔑] Exchanging code for tokens...")
    token_response = exchange_code_for_token(auth_code, verifier)

    print("✅ Tokens received:")
    print("access_token:", token_response.get('access_token'))
    print("refresh_token:", token_response.get('refresh_token'))
    print("expires_in:", token_response.get('expires_in'))


if __name__ == "__main__":
    main()

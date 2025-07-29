import requests
import os

# 🔧 Config
PAGE_ACCESS_TOKEN = "your_page_access_token"
FACEBOOK_PAGE_ID = "your_page_id"
INSTAGRAM_ACCOUNT_ID = "your_instagram_business_id"
IMAGE_PATH = "output.png"

# Example data from your article fetch
headline = "Ozzy Osbourne dies at 76, weeks after farewell Black Sabbath concert"
article_url = "https://example.com/ozzy-osbourne-dies"

# 🧾 Generate caption
CAPTION = f"📰 {headline}\n\nRead more: {article_url}"


def post_to_facebook(image_path, caption):
    print("[Facebook] Uploading image...")
    url = f"https://graph.facebook.com/v19.0/{FACEBOOK_PAGE_ID}/photos"
    files = {
        'source': open(image_path, 'rb')
    }
    data = {
        'caption': caption,
        'access_token': PAGE_ACCESS_TOKEN
    }

    response = requests.post(url, files=files, data=data)
    if response.ok:
        print("✅ Posted to Facebook.")
    else:
        print(f"❌ Facebook error: {response.text}")


def post_to_instagram(image_url, caption):
    print("[Instagram] Uploading image...")

    # 1. Create IG media object
    media_url = f"https://graph.facebook.com/v19.0/{INSTAGRAM_ACCOUNT_ID}/media"
    payload = {
        'image_url': image_url,
        'caption': caption,
        'access_token': PAGE_ACCESS_TOKEN
    }

    res = requests.post(media_url, data=payload)
    if not res.ok:
        print(f"❌ IG Create Media Error: {res.text}")
        return

    creation_id = res.json().get('id')

    # 2. Publish the media
    publish_url = f"https://graph.facebook.com/v19.0/{INSTAGRAM_ACCOUNT_ID}/media_publish"
    res = requests.post(publish_url, data={
        'creation_id': creation_id,
        'access_token': PAGE_ACCESS_TOKEN
    })

    if res.ok:
        print("✅ Posted to Instagram.")
    else:
        print(f"❌ IG Publish Error: {res.text}")


# 🔁 Run
if __name__ == "__main__":
    if os.path.exists(IMAGE_PATH):
        post_to_facebook(IMAGE_PATH, CAPTION)

        # Instagram needs hosted URL
        hosted_image_url = "https://yourdomain.com/images/output.png"  # Must be HTTPS and public
        post_to_instagram(hosted_image_url, CAPTION)
    else:
        print("❌ Image not found.")

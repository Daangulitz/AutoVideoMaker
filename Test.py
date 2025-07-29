import tweepy

API_KEY = 'XmgJycvux8I3i6OJvi9w1Eyrx'
API_SECRET = 'sGcby470r6N8CmBwblNalJSFAwWoKEowe5h6cgq0IJ3ULgfSIp'
ACCESS_TOKEN = '1948437875785338880-UdCvuMYyTRn3PwHmM4MfrhBiDz8rGQ'
ACCESS_SECRET = 'vrMTw2a3hFOyV2fNNmV7FPUr7sSDTEXQ5gpRFFLGDRJ5s'

auth = tweepy.OAuth1UserHandler(API_KEY, API_SECRET, ACCESS_TOKEN, ACCESS_SECRET)
api = tweepy.API(auth)

try:
    media = api.media_upload("output_2.png")
    tweet = api.update_status(status="Test tweet with image", media_ids=[media.media_id])
    print(f"Posted tweet: https://twitter.com/user/status/{tweet.id}")
except Exception as e:
    print(f"Error: {e}")

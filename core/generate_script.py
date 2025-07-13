import os
import requests

API_TOKEN = os.getenv("HUGGINGFACE_API_TOKEN") or "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"
API_URL = "https://api-inference.huggingface.co/models/gpt2"

headers = {"Authorization": f"Bearer {API_TOKEN}"}

def query_huggingface(payload):
    response = requests.post(API_URL, headers=headers, json=payload)
    if response.status_code !=200:
        raise Exception(f"API Error: {response.status_code} - {response.text}")
    return response.json()

def generate_video_script(articles):
    prompt = "You are a news anchor. Summarize these news stories in a natural, engaging style fit for a 1-minute video narration:\n\n"
    for i, article in enumerate(articles, 1):
        prompt += f"{i}. Title: {article.get('title', '')}\n"
        if article.get('description'):
            prompt += f"Description{article['description']}\n"
        prompt += "\n"
    prompt += "Narration Script:"

    payload = {
            "inputs": prompt,
        "parameters": {
            "max_length": 150,
            "temperature": 0.7,
            "top_p": 0.9,
            "return_full_text": False,
            "num_return_sequences": 1,
        }
    }

    output = query_huggingface(payload)

    if isinstance(output, list) and len(output) > 0 and "generated_text" in output[0]:
        return output[0]["generated"]
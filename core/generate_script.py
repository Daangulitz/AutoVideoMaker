import os
import requests

from transformers import pipeline, set_seed

# Load the local GPT-2 text generation pipeline
pipe = pipeline("text-generation", model="openai-community/gpt2")
set_seed(42)  # Optional: makes output consistent

def generate_video_script(articles):
    """
    Generate a video narration script from news articles using GPT-2 locally.

    Args:
        articles (list of dict): Each with 'title' and optionally 'description'.

    Returns:
        str: Generated video narration script.
    """
    prompt = "Write a short, natural-sounding 1-minute news script summarizing the following headlines:\n\n"
    
    for i, article in enumerate(articles, 1):
        prompt += f"{i}. Title: {article['title']}\n"
        if article.get("description"):
            prompt += f"   Description: {article['description']}\n"
    prompt += "\nNarration Script:\n"

    result = pipe(prompt, max_length=200, num_return_sequences=1)[0]["generated_text"]

    # Strip everything before the actual narration if needed
    return result.split("Narration Script:")[-1].strip()

if __name__ == "__main__":
    sample_articles = [
        {
            "title": "Markets rally as inflation slows",
            "description": "Markets are seeing gains as inflation numbers come in lower than expected."
        },
        {
            "title": "AI breakthroughs announced",
            "description": "New large language models are pushing the limits of artificial intelligence."
        },
        {
            "title": "World leaders reach climate deal",
            "description": "Historic agreement made at the summit to cut global emissions by 40%."
        }
    ]

    script = generate_video_script(sample_articles)
    print("Generated Video Script:\n")
    print(script)
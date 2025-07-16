# core/generate_script.py

from transformers import pipeline

# Initialize once globally to save loading time
pipe = pipeline("text-generation", model="openai-community/gpt2", max_length=150)

def generate_script(article):
    """
    Generate a short script/narration text based on a single news article dict.
    Uses title and description/content to form a prompt for the text generation model.
    
    Args:
        article (dict): News article with keys like 'title' and 'description'.
        
    Returns:
        str: Generated script text.
    """
    title = article.get("title", "No title")
    description = article.get("description") or article.get("content") or ""

    prompt = (
        f"Write a short, engaging video script based on this news headline and description:\n\n"
        f"Title: {title}\n"
        f"Description: {description}\n\n"
        f"Script:"
    )
    
    # Run the text generation model on the prompt
    result = pipe(prompt, max_length=150, num_return_sequences=1)
    
    # Extract generated text from result
    generated_text = result[0]['generated_text']
    
    # Remove prompt from the output (keep only generated part after prompt)
    script = generated_text[len(prompt):].strip()
    
    # Optional: Limit script length or do cleanup here
    return script

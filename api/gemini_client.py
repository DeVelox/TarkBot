import os
from google.generativeai.client import configure
from google.generativeai.generative_models import GenerativeModel


def init_gemini():
    """Initialize Gemini model with API key from environment."""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError(
            "GEMINI_API_KEY environment variable not set. Please add it to .env file."
        )

    configure(api_key=api_key)
    return GenerativeModel(model_name="gemini-2.0-flash-lite")


def generate_response(model, prompt):
    """Generate response using Gemini model."""
    response = model.generate_content(prompt)
    return response.text


def extract_item_name(model, query):
    """Extract item name from freeform query using Gemini."""
    prompt = f"Extract the most likely Escape from Tarkov item name from this query: '{query}'. Return only the item name, nothing else."
    response = model.generate_content(prompt)
    return response.text.strip()

import os
from groq import Groq


def init_groq():
    """Initialize Groq client with API key from environment."""
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError(
            "GROQ_API_KEY environment variable not set. Please add it to .env file."
        )

    return Groq(api_key=api_key)


def generate_response(client, json_data):
    """Generate response using Groq model."""
    response = client.chat.completions.create(
        model="openai/gpt-oss-20b",
        messages=[
            {"role": "system", "content": "Transform the given JSON input containing Tarkov item information into a concise, accurate, and natural-sounding sentence, optimized for text-to-speech, without any extra formatting. Use the sell price in Rubles from the flea market as the item's price. Indicate the required quantity for quests or hideout upgrades. Clearly state if the item needs to be found in raid."},
            {"role": "user", "content": json_data},
        ],
        temperature=0,
        max_completion_tokens=300,
        top_p=0.5,
        reasoning_effort="low",
        stream=False,
        stop=None,
    )
    return response.choices[0].message.content.strip()


def extract_item_name(client, query):
    """Extract item name from freeform query using Groq."""
    response = client.chat.completions.create(
        model="openai/gpt-oss-20b",
        messages=[
            {"role": "system", "content": "Extract only the Tarkov item name from the sentence below, without any extra formatting."},
            {"role": "user", "content": query},
        ],
        max_completion_tokens=150,
        temperature=0,
        top_p=0.5,
        reasoning_effort="low",
        stream=False,
        stop=None,
    )
    item_name = response.choices[0].message.content.strip()
    # Clean up common issues
    item_name = item_name.strip('"').strip("'")
    if not item_name or item_name.lower() == "unknown":
        return None
    return item_name

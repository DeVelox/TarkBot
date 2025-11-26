import json
from api.groq_client import init_groq, generate_response


def format_response(data, query_name):
    """Format item data into a concise factual response using Groq."""
    if not data:
        return "Item not found."

    # Prepare structured data
    structured = {
        "item_name": query_name,
        "flea_price": data["flea_price"],
        "quests": data.get("quests", []),
        "hideouts": data.get("hideouts", []),
    }

    data_json = json.dumps(structured)

    model = init_groq()
    return generate_response(model, data_json)

from api.gemini_client import init_gemini, generate_response


def format_response(data):
    """Format item data into a natural language response using Gemini."""
    if not data:
        return "Sorry, I couldn't find information about that item."

    item = data["item"]
    quests = data["quests"]

    prompt = f"""
    Format this Escape from Tarkov item information into a natural, conversational response for a player asking about the item:

    Item: {item["name"]} ({item["shortName"]})

    Pricing:
    - Flea market average (24h): {item.get("avg24hPrice", "N/A")}
    - Base price: {item["basePrice"]}
    - Vendor sell prices:
"""

    for sell in item.get("sellFor", []):
        prompt += f"      - {sell['source'].title()}: {sell['price']}\n"

    if quests:
        prompt += "\n    Quest requirements:\n"
        for quest in quests:
            fir_note = " (must be Found in Raid)" if quest["found_in_raid"] else ""
            prompt += f"      - {quest['quest_name']} ({quest['trader']}): {quest['count']} needed{fir_note}\n"
    else:
        prompt += "\n    No active quest requirements found for this item.\n"

    prompt += """
    Provide a brief, direct response with no pleasantries or preludes. Format like: "Item costs X on flea, Y from vendor. N needed for quest Q from trader T (FIR if applicable)." Include only essential pricing and quest info in natural sentences, using exact numbers from the API.
    """

    model = init_gemini()
    return generate_response(model, prompt)

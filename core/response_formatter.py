def format_response(data):
    """Format item data into a brief factual response."""
    if not data:
        return "Item not found."

    item = data["item"]
    flea_price = data.get("flea_price", "N/A")
    quests = data.get("quests", [])
    hideouts = data.get("hideouts", [])

    response = f"{item['shortName']} sells for {flea_price} on flea"

    for quest in quests:
        amount = quest["count"]
        verb = "is" if amount == 1 else "are"
        fir_note = " You need them found in raid." if quest["found_in_raid"] else ""
        response += f". {amount} {verb} needed for {quest['quest_name']} from {quest['trader']}{fir_note}"

    for hideout in hideouts:
        amount = hideout["count"]
        verb = "is" if amount == 1 else "are"
        response += f". {amount} {verb} needed for {hideout['hideout_name']} level {hideout['level']}"

    return response

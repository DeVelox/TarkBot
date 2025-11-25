from core.tarkov_api_client import get_items_by_name, get_tasks


def find_item(name):
    """Find the best matching item by name."""
    items = get_items_by_name(name)
    if not items:
        return None
    # For MVP, return the first match
    return items[0]


def get_quests_for_item(item_name):
    """Get quests that require the specified item."""
    tasks = get_tasks()
    relevant_tasks = []
    for task in tasks:
        for obj in task.get("objectives", []):
            if (
                isinstance(obj, dict)
                and "item" in obj
                and obj["item"]["name"] == item_name
            ):
                relevant_tasks.append(
                    {
                        "quest_name": task["name"],
                        "trader": task["trader"]["name"]
                        if task.get("trader")
                        else "Unknown",
                        "count": obj.get("count", 1),
                        "found_in_raid": obj.get("foundInRaid", False),
                    }
                )
    return relevant_tasks


def get_item_data(name):
    """Get complete item data including pricing and quest requirements."""
    item = find_item(name)
    if not item:
        return None

    quests = get_quests_for_item(item["name"])
    return {"item": item, "quests": quests}

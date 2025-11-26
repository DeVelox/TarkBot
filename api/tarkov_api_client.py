import requests
import pickle
import os
import difflib

CACHE_DIR = "cache"
os.makedirs(CACHE_DIR, exist_ok=True)


def query_graphql(query):
    """Execute GraphQL query against Tarkov.dev API."""
    url = "https://api.tarkov.dev/graphql"
    payload = {"query": query}
    response = requests.post(url, json=payload)
    response.raise_for_status()
    return response.json()


def get_hideouts():
    """Get hideout stations with disk-cached data."""
    cache_file = os.path.join(CACHE_DIR, "hideouts.pkl")
    if os.path.exists(cache_file):
        with open(cache_file, "rb") as f:
            return pickle.load(f)
    query = """
    {
        hideoutStations(gameMode: regular, lang: en) {
            name
            levels {
                level
                itemRequirements {
                    item {
                        id
                    }
                    count
                }
            }
        }
    }
    """
    data = query_graphql(query)
    hideouts = data["data"]["hideoutStations"]
    with open(cache_file, "wb") as f:
        pickle.dump(hideouts, f)
    return hideouts


def get_all_items():
    """Get all items with disk-cached data."""
    cache_file = os.path.join(CACHE_DIR, "items.pkl")
    if os.path.exists(cache_file):
        with open(cache_file, "rb") as f:
            return pickle.load(f)
    query = """
    {
        items(lang: en, gameMode: regular) {
            id
            name
            shortName
            sellFor {
                vendor {
                    name
                }
            }
            usedInTasks {
              id
            }
        }
    }
    """
    data = query_graphql(query)
    items = data["data"]["items"]
    with open(cache_file, "wb") as f:
        pickle.dump(items, f)
    return items


def get_tasks():
    """Get tasks with disk-cached data."""
    cache_file = os.path.join(CACHE_DIR, "tasks.pkl")
    if os.path.exists(cache_file):
        with open(cache_file, "rb") as f:
            return pickle.load(f)
    query = """
    {
        tasks(gameMode: regular, lang: en) {
            name
            trader {
                name
            }
            objectives {
                type
                ... on TaskObjectiveItem {
                    items {
                        id
                    }
                    foundInRaid
                    count
                }
                ... on TaskObjectiveBuildItem {
                    item {
                        id
                    }
                }
            }
        }
    }
    """
    data = query_graphql(query)
    tasks = data["data"]["tasks"]
    with open(cache_file, "wb") as f:
        pickle.dump(tasks, f)
    return tasks


def get_item_data(name):
    """Get item data with fresh price, using cached metadata."""
    all_items = get_all_items()
    name_lower = name.lower()
    words = name_lower.split()

    # First, try exact substring matches
    substring_matches = [
        item for item in all_items if name_lower in item["name"].lower()
    ]
    if substring_matches:
        matching_items = substring_matches
    else:
        # Fall back to multi-word matching
        matching_items = [
            item
            for item in all_items
            if all(word in item["name"].lower() for word in words)
        ]
        if not matching_items:
            return None

    # Prioritize items with more usedInTasks, then by name length (shorter names first)
    matching_items.sort(key=lambda x: (-len(x.get("usedInTasks", [])), len(x["name"])))
    item = matching_items[0]
    item_id = item["id"]

    # Query fresh price
    query = f'''{{
        items(ids: ["{item_id}"], lang: en, gameMode: regular) {{
            sellFor {{
                priceRUB
                vendor {{
                    name
                }}
            }}
        }}
    }}'''
    data = query_graphql(query)
    items_data = data["data"]["items"]
    if not items_data:
        return None
    item_data = items_data[0]

    # Find flea price
    flea_price = None
    for sell in item_data.get("sellFor", []):
        if sell["vendor"]["name"].lower() == "flea market":
            flea_price = sell["priceRUB"]
            break

    if not flea_price:
        return None  # Only return if on flea

    # Get quests from cache
    tasks = get_tasks()
    quests = []
    for task in tasks:
        for obj in task.get("objectives", []):
            item_ids = []
            if "item" in obj:
                item_ids.append(obj["item"]["id"])
            elif "items" in obj:
                item_ids.extend(i["id"] for i in obj["items"])
            if (
                "give" in obj.get("type", "") or "build" in obj.get("type", "")
            ) and item_id in item_ids:
                quests.append(
                    {
                        "quest_name": task["name"],
                        "trader": task["trader"]["name"]
                        if task.get("trader")
                        else "Unknown",
                        "count": obj.get("count", 1),
                        "found_in_raid": obj.get("foundInRaid", False),
                    }
                )

    # Get hideouts from cache
    hideouts = get_hideouts()
    hideout_reqs = []
    for station in hideouts:
        for level in station.get("levels", []):
            for req in level.get("itemRequirements", []):
                if req["item"]["id"] == item_id:
                    hideout_reqs.append(
                        {
                            "hideout_name": station["name"],
                            "level": level["level"],
                            "count": req["count"],
                        }
                    )

    return {
        "item": item,
        "flea_price": flea_price,
        "quests": quests,
        "hideouts": hideout_reqs,
    }

import requests
import pickle
import os

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
                    count
                    item {
                        id
                    }
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
                ... on TaskObjectiveItem {
                    items {
                        id
                    }
                    foundInRaid
                    count
                }
                type
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
    """Get item data with price, using cached quests and hideouts."""
    query = f'''{{
        items(lang: en, name: "{name}", gameMode: regular) {{
            id
            name
            shortName
            sellFor {{
                priceRUB
                vendor {{
                    name
                }}
            }}
        }}
    }}'''
    data = query_graphql(query)
    items = data["data"]["items"]
    if not items:
        return None
    item = items[0]  # Assume first match
    item_id = item["id"]

    # Find flea price
    flea_price = None
    for sell in item.get("sellFor", []):
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
            if obj.get("type") == "giveItem" and any(
                i["id"] == item_id for i in obj.get("items", [])
            ):
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

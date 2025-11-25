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
            usedInTasks {{
                id
            }}
        }}
    }}'''
    data = query_graphql(query)
    items = data["data"]["items"]
    if not items:
        return None
    # Prioritize items with usedInTasks
    items.sort(key=lambda x: len(x.get("usedInTasks", [])), reverse=True)
    item = items[0]
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

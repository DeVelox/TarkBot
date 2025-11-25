import requests


def query_graphql(query):
    """Execute GraphQL query against Tarkov.dev API."""
    url = "https://api.tarkov.dev/graphql"
    payload = {"query": query}
    response = requests.post(url, json=payload)
    response.raise_for_status()
    return response.json()


def get_items_by_name(name):
    """Get items matching the name."""
    query = f'''{{
        itemsByName(name: "{name}") {{
            name
            shortName
            avg24hPrice
            basePrice
            sellFor {{
                price
                source
            }}
        }}
    }}'''
    data = query_graphql(query)
    return data["data"]["itemsByName"]


def get_tasks():
    """Get all tasks with item objectives."""
    query = """
    {
        tasks {
            name
            trader {
                name
            }
            objectives {
                ... on TaskObjectiveItem {
                    item {
                        name
                    }
                    count
                    foundInRaid
                }
            }
        }
    }
    """
    data = query_graphql(query)
    return data["data"]["tasks"]

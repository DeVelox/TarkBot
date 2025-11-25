import click
import json
from core.tarkov_api_client import get_item_data
from core.response_formatter import format_response


@click.group()
def cli():
    """TarkBot CLI for Escape from Tarkov item information."""
    pass


@cli.command()
@click.argument("question")
@click.option("--debug", is_flag=True, help="Output structured JSON data")
def ask(question, debug):
    """Ask a question about a Tarkov item (MVP: treat as item name)."""
    click.echo(f"Searching for: {question}")
    data = get_item_data(question)
    if debug:
        if not data:
            click.echo("Item not found.")
            return
        result = {
            "item_name": data["item"]["name"],
            "flea_price": data["flea_price"],
            "quests": [
                {
                    "quest_name": q["quest_name"],
                    "trader": q["trader"],
                    "count": q["count"],
                    "found_in_raid": q["found_in_raid"],
                }
                for q in data.get("quests", [])
            ],
            "hideouts": [
                {
                    "hideout_name": h["hideout_name"],
                    "level": h["level"],
                    "count": h["count"],
                }
                for h in data.get("hideouts", [])
            ],
        }
        click.echo(json.dumps(result, indent=2))
    else:
        response = format_response(data, question)
        click.echo(response)


@cli.command()
@click.option("--debug", is_flag=True, help="Output structured JSON data")
def test(debug):
    """Run automated tests on sample items."""
    test_items = [
        "Glock 17",  # Not needed for any quests
        "MRE",  # Needed for quests but not FIR
        "MP-133",  # Needed for quests but not FIR
        "Cat figurine",  # Needed for quests with FIR
        "Augmentin antibiotic pills",  # Needed for quests with FIR
    ]

    for item in test_items:
        click.echo(f"\n--- Testing: {item} ---")
        data = get_item_data(item)
        if debug:
            if not data:
                click.echo("Item not found.")
                continue
            result = {
                "item_name": data["item"]["name"],
                "flea_price": data["flea_price"],
                "quests": [
                    {
                        "quest_name": q["quest_name"],
                        "trader": q["trader"],
                        "count": q["count"],
                        "found_in_raid": q["found_in_raid"],
                    }
                    for q in data.get("quests", [])
                ],
                "hideouts": [
                    {
                        "hideout_name": h["hideout_name"],
                        "level": h["level"],
                        "count": h["count"],
                    }
                    for h in data.get("hideouts", [])
                ],
            }
            click.echo(json.dumps(result, indent=2))
        else:
            response = format_response(data, item)
            click.echo(f"Response: {response}")

    click.echo("\n--- Test completed ---")

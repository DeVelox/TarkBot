import click
import json
from core.tarkov_api_client import get_item_data
from core.response_formatter import format_response
from api.groq_client import init_groq, extract_item_name


@click.group()
def cli():
    """TarkBot CLI for Escape from Tarkov item information."""
    pass


@cli.command()
@click.argument("question")
@click.option("--debug", is_flag=True, help="Output structured JSON data")
def ask(question, debug):
    """Ask a question about a Tarkov item."""
    click.echo(f"Query: {question}")
    model = init_groq()
    item_name = extract_item_name(model, question)
    click.echo(f"Extracted item: {item_name}")
    data = get_item_data(item_name)
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
        response = format_response(data, item_name)
        click.echo(response)


@cli.command()
@click.option("--debug", is_flag=True, help="Output structured JSON data")
def test(debug):
    """Run automated tests on sample queries."""
    test_queries = [
        "Do I need Glock 17?",  # Not needed for any quests
        "How much is MRE?",  # Needed for quests but not FIR
        "Do I need MP-133?",  # Needed for quests but not FIR
        "How much is cat figurine?",  # Needed for quests with FIR
        "Do I need Augmentin antibiotic pills?",  # Needed for quests with FIR
    ]

    for query in test_queries:
        click.echo(f"\n--- Testing: {query} ---")
        model = init_groq()
        item_name = extract_item_name(model, query)
        click.echo(f"Extracted item: {item_name}")
        if not item_name:
            click.echo("No item extracted.")
            continue
        data = get_item_data(item_name)
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
            response = format_response(data, item_name)
            click.echo(f"Response: {response}")

    click.echo("\n--- Test completed ---")

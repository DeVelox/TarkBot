import click
from core.item_lookup import get_item_data
from core.response_formatter import format_response


@click.group()
def cli():
    """TarkBot CLI for Escape from Tarkov item information."""
    pass


@cli.command()
@click.argument("question")
@click.option("--debug", is_flag=True, help="Output raw API response for debugging")
def ask(question, debug):
    """Ask a question about a Tarkov item (MVP: treat as item name)."""
    click.echo(f"Searching for: {question}")
    data = get_item_data(question)
    if debug:
        click.echo("Raw API data:")
        click.echo(data)
    response = format_response(data)
    click.echo(response)

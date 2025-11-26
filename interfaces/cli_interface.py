import click
import json
import sys
import os
from core.tarkov_api_client import get_item_data
from core.response_formatter import format_response
from core.voice_interface import get_voice_input, synthesize_speech
from api.groq_client import init_groq, extract_item_name


def wait_for_tilde():
    """Wait for tilde key press in a cross-platform way."""
    if os.name == "nt":  # Windows - use input for focus-independent operation
        while True:
            try:
                response = input("Press '~' to speak, or 'q' to quit: ").strip().lower()
                if response in ["`", "~", "tilde", "speak"]:
                    return True
                elif response in ["q", "quit", "exit"]:
                    return False
            except (KeyboardInterrupt, EOFError):
                return False
    else:
        # Unix-like systems (Linux, macOS) - try raw input first, fallback to input
        click.echo("Press '~' to speak, or 'q' to quit...")
        try:
            import termios
            import tty

            fd = sys.stdin.fileno()
            old_settings = termios.tcgetattr(fd)

            try:
                tty.setraw(fd)
                while True:
                    char = sys.stdin.read(1)
                    if char == "`" or char == "~":
                        return True
                    elif char.lower() == "q":
                        return False
            finally:
                termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

        except ImportError:
            pass

    # Fallback for any system that doesn't support raw input
    while True:
        try:
            response = input("Press '~' to speak, or 'q' to quit: ").strip().lower()
            if response in ["`", "~", "tilde", "speak"]:
                return True
            elif response in ["q", "quit", "exit"]:
                return False
        except (KeyboardInterrupt, EOFError):
            return False
    try:
        import termios
        import tty

        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)

        try:
            tty.setraw(fd)
            while True:
                char = sys.stdin.read(1)
                if char == "`" or char == "~":
                    return True
                elif char.lower() == "q":
                    return False
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

    except ImportError:
        pass

    # Fallback: use input with prompt
    while True:
        try:
            response = input("Press '~' to speak, or 'q' to quit: ").strip().lower()
            if response in ["`", "~", "tilde", "speak"]:
                return True
            elif response in ["q", "quit", "exit"]:
                return False
        except (KeyboardInterrupt, EOFError):
            return False


@click.group()
def cli():
    """TarkBot CLI for Escape from Tarkov item information."""
    pass


@cli.command()
@click.argument("question", required=False)
@click.option("--voice", is_flag=True, help="Use voice input instead of text")
@click.option("--debug", is_flag=True, help="Output structured JSON data")
def ask(question, voice, debug):
    """Ask a question about a Tarkov item."""
    if voice:
        while True:
            # Wait for tilde key press
            if not wait_for_tilde():
                click.echo("Exiting voice mode.")
                return
            click.echo("Listening for 5 seconds...")
            question = get_voice_input(duration=5)

            if not question:
                click.echo("No speech detected.")
                continue

            click.echo(f"Query: {question}")
            model = init_groq()
            item_name = extract_item_name(model, question)
            click.echo(f"Item: {item_name}")
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
                click.echo(response)
                synthesize_speech(response)

    # Text mode (existing logic)
    if not question:
        click.echo("No question provided.")
        return

    click.echo(f"Query: {question}")
    model = init_groq()
    item_name = extract_item_name(model, question)
    click.echo(f"Item: {item_name}")
    if not item_name:
        click.echo("No item extracted.")
        return
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
        click.echo(f"Item: {item_name}")
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

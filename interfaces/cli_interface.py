import click
import json
import sys
import os
import tomllib
from core.tarkov_api_client import get_item_data
from core.response_formatter import format_response
from api.groq_client import init_groq, extract_item_name


def load_config():
    """Load keybind config from config.toml, with defaults."""
    config_path = "config.toml"
    defaults = {"keybinds": {"speak": "ctrl+`", "quit": "ctrl+q"}}
    if os.path.exists(config_path):
        with open(config_path, "rb") as f:
            config = tomllib.load(f)
        # Merge with defaults
        for key, value in defaults["keybinds"].items():
            config.get("keybinds", {}).setdefault(key, value)
        return config
    return defaults


def wait_for_tilde():
    """Wait for configured keybinds to speak or quit using pynput."""
    from pynput import keyboard

    config = load_config()
    speak_key = config["keybinds"]["speak"]
    quit_key = config["keybinds"]["quit"]

    # Convert config format to pynput format
    def format_key(key_str):
        if "+" in key_str:
            parts = key_str.split("+")
            modifiers = parts[:-1]
            key = parts[-1]
            modifier_str = "+".join(f"<{mod}>" for mod in modifiers)
            if modifiers:
                return f"{modifier_str}+{key}"
            else:
                return key
        else:
            return key_str

    speak_key_formatted = format_key(speak_key)
    quit_key_formatted = format_key(quit_key)

    click.echo(f"Press '{speak_key}' to speak, or '{quit_key}' to quit...")

    speak_pressed = False
    quit_pressed = False

    def on_speak():
        nonlocal speak_pressed
        speak_pressed = True
        hotkeys.stop()

    def on_quit():
        nonlocal quit_pressed
        quit_pressed = True
        hotkeys.stop()

    hotkeys = keyboard.GlobalHotKeys(
        {speak_key_formatted: on_speak, quit_key_formatted: on_quit}
    )

    hotkeys.start()

    try:
        hotkeys.join()
        if speak_pressed:
            return True
        elif quit_pressed:
            return False
        else:
            return False
    except KeyboardInterrupt:
        hotkeys.stop()
        return False
    else:
        return False


@click.group(invoke_without_command=True)
@click.pass_context
def cli(ctx):
    """TarkBot CLI for Escape from Tarkov item information."""
    if ctx.invoked_subcommand is None:
        # No subcommand provided, default to voice mode
        ctx.invoke(ask, question=None, voice=True, debug=False)


@cli.command()
@click.argument("question", required=False)
@click.option("--voice", is_flag=True, help="Use voice input instead of text")
@click.option("--debug", is_flag=True, help="Output structured JSON data")
def ask(question, voice, debug):
    """Ask a question about a Tarkov item."""
    from core.voice_interface import synthesize_speech

    if voice:
        from core.voice_interface import get_voice_input

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

#!/usr/bin/env python3
"""
TarkBot Main Entry Point
"""

import sys
from interfaces.cli_interface import cli, TarkBotCLI


def main():
    # Handle default ask command when just a question is provided
    if len(sys.argv) == 2 and not sys.argv[1].startswith("-"):
        # This looks like a question, not a command
        question = sys.argv[1]
        bot = TarkBotCLI()
        bot.ask_question(question)
    else:
        # Use the normal CLI
        cli()


if __name__ == "__main__":
    main()

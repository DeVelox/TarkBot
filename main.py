#!/usr/bin/env python3
"""
TarkBot Main Entry Point
"""

from dotenv import load_dotenv
from interfaces.cli_interface import cli

# Load environment variables
load_dotenv()


if __name__ == "__main__":
    cli()

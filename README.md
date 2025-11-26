# TarkBot

A voice-powered item lookup tool for Escape from Tarkov, built using the free models in [OpenCode](https://github.com/sst/opencode).

## What is this?

Listening to my friends playing Tarkov, I decided to make a prototype for a smarter voice-based item lookup app. It uses LLMs only for text and voice processing while still fetching API data traditionally for accuracy.

## Features

- Voice input with natural language queries
- Real-time pricing from Tarkov.dev API
- Quest requirement checking
- Configurable keybinds

## Installation

### Linux/macOS (Development)

```bash
# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# Clone and setup
git clone <your-repo-url>
cd tarkbot
uv sync
uv run main.py
```

### Windows (Recommended)

Download the latest `TarkBot-Windows.zip` from [Releases](https://github.com/your-username/tarkbot/releases), extract it, and run `TarkBot.exe`.

## Configuration

1. Copy `.env-example` to `.env` and add your Groq API key:
   ```
   GROQ_API_KEY=your_key_here
   ```

2. Edit `config.toml` to customize keybinds if needed.

## Usage

- **Text mode**: `uv run main.py ask "price of AK-74N"`
- **Voice mode**: `uv run main.py` (defaults to voice)
- **Debug output**: Add `--debug` for JSON output

## Windows Defender

The executable is unsigned, so Windows might show a warning. You can add `TarkBot.exe` to Windows Defender exclusions if needed.

## License

MIT
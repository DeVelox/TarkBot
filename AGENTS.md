# TarkBot AI Agent Implementation Plan

## Project Overview
Build an AI agent that provides item pricing and quest requirement information for Escape from Tarkov using the tarkov.dev API, with natural language responses powered by Groq AI.

---

## Phase 1: Project Setup & Core Infrastructure

### Step 1.1: Project Structure ✅ UPDATED
**Choice**: Modular structure optimized for API-based item lookup
```
tarkbot/
├── core/
│   ├── __init__.py
│   ├── tarkov_api_client.py    # tarkov.dev GraphQL API wrapper
│   ├── item_lookup.py          # Item search and data processing
│   └── response_formatter.py   # Gemini-powered natural responses
├── interfaces/
│   ├── __init__.py
│   ├── cli_interface.py        # CLI commands (text input/output)
│   └── voice_interface.py      # Voice I/O (stage 2)
├── api/
│   ├── __init__.py
│   └── gemini_client.py        # Gemini API client
├── main.py                     # Entry point
└── .env                        # API keys
```

### Step 1.2: Dependencies ✅ UPDATED
**Choice**: Minimal dependencies focused on API integration and voice
```
click>=8.3.1
groq>=0.9.0
numpy>=1.24.0
sounddevice>=0.4.6
soundfile>=0.12.0
python-dotenv>=1.2.1
requests>=2.32.5
```

### Step 1.3: Package Manager ✅ CONFIRMED
**Choice**: uv (Modern, fast, all-in-one Python package manager)

---

## Phase 2: API Integration & Data Processing

### Step 2.1: Data Source ✅ UPDATED
**Choice**: tarkov.dev GraphQL API (official data source)
- **Real-time item data** from official API
- **Pricing information**: vendor prices, flea market prices
- **Quest requirements**: items needed for quests with FIR status
- **Trader information**: all trader cash offers and prices
- **Barter trades**: what items are used for/obtained from barters
- **No local storage needed**: API provides current data

### Step 2.2: API Strategy ✅ CONFIRMED
**Choice**: Direct API integration with caching
- Query tarkov.dev GraphQL API for item data
- Local response caching for performance
- Real-time pricing and quest information
- No scraping or local data maintenance

### Step 2.3: Data Structure ✅ UPDATED
**Choice**: API response format with natural language processing
```python
{
    "item_name": "Cat figurine",
    "vendor_price": 12000,
    "vendor_trader": "Prapor",
    "flea_price": 8500,
    "quest_requirements": [
        {
            "quest_name": "Collector",
            "trader": "Jaeger",
            "found_in_raid": True
        }
    ]
}
```

---

## Phase 3: Query Processing & LLM Integration

### Step 3.1: LLM Provider ✅ UPDATED
**Choice**: Groq with OpenAI GPT-OSS-20B
- Fast inference with Groq platform
- Advanced reasoning for item extraction and response formatting
- Generous free tier
- Access to OpenAI models via Groq

### Step 3.2: Query Classification ✅ UPDATED
**Choice**: Direct item extraction from natural language
- Extract item names from user questions
- Query tarkov.dev API for item data
- Filter for pricing and quest requirements
- Simple and efficient processing

### Step 3.3: Response Generation ✅ UPDATED
**Choice**: Natural language formatting with Groq
- Format API data into conversational responses
- Handle different question types naturally
- Include vendor price, flea price, and quest info (if applicable)
- Short, concise responses with only relevant information in natural sentences, not data dumps

---

## Phase 4: Voice Integration (Stage 2)

### Step 4.1: Speech-to-Text ✅ IMPLEMENTED
**Choice**: Groq Whisper Large V3 Turbo
- High-quality transcription via Groq API
- Optimized for English Tarkov queries
- Low latency with fast inference
- No local model required

### Step 4.2: Text-to-Speech ✅ IMPLEMENTED
**Choice**: Groq PlayAI TTS
- High-quality voice synthesis via Groq API
- Natural-sounding responses
- Fast inference
- Integrated with voice input flow

### Step 4.3: Voice Interface Logic ✅ IMPLEMENTED
**Choice**: Integrated voice/text interaction
- Voice input → Voice output (automatic)
- Voice input → Text output (--debug flag)
- Text input → Text output (default)
- Audio recording with sounddevice
- TTS playback with soundfile

---

## Phase 5: CLI Interface Development

### Step 5.1: CLI Framework ✅ CONFIRMED
**Choice**: Click framework
- Professional CLI with commands, options, help
- Better user experience
- Command structure for development and testing

### Step 5.2: Command Structure ✅ UPDATED
**Choice**: Simple item inquiry commands
```bash
# Development phase (text only)
uv run main.py "Do I need cat figurine?"
uv run main.py "price of AK-74N"
uv run main.py "LEDX price"

# Stage 2 (voice support)
uv run main.py --voice "Do I need cat figurine?"
uv run main.py --voice --no-speak "price of AK-74N"  # Voice input, text output
```

---

## Phase 6: Testing & Validation

### Step 6.1: Test Data ✅ CONFIRMED
**Choice**: Option C (Minimal test suite)
- Core functionality tests only
- Sample Tarkov queries
- Quick validation

### Step 6.2: Validation Metrics ✅ CONFIRMED
**Choice**: Option C (Basic metrics)
- Response time tracking
- Simple accuracy checks
- Source verification
- Data to support user feedback

---

## Phase 7: Future Expansion (Discord & Voice)

### Step 7.1: Discord Integration
**Planned**: Text commands only initially
- `!ask best ammo for 5.45`
- Simple text responses
- Same core logic as CLI

### Step 7.2: Voice Integration
**Planned**: Full voice conversation
- Speech-to-text (Google Speech-to-Text API - free tier)
- Text-to-speech (ElevenLabs/OpenAI TTS)
- Natural voice interaction

---

## Implementation Order

1. **Week 1**: Setup + Core API integration + Item lookup
2. **Week 2**: Response formatting + CLI interface
3. **Week 3**: Testing + Optimization
4. **Week 4**: Voice integration (optional)
5. **Week 5**: Discord bot (optional)

---

## Key Technical Decisions

### Architecture
- **Modular design** for easy interface swapping
- **Separation of concerns** between core logic and interfaces
- **Unified response format** for all interfaces

### Data Management
- **API-first approach** using official tarkov.dev GraphQL API
- **Real-time pricing** from live flea market data
- **Quest integration** with Found in Raid status checking
- **No local storage** - API provides current data

### Performance
- **Direct item extraction** from natural language queries
- **Gemini-powered formatting** for natural responses
- **API caching** for performance optimization
- **Basic metrics** for response time tracking

---

## Success Criteria

- [ ] Can provide vendor and flea market prices for items
- [ ] Can identify quest requirements with FIR status
- [ ] Provides natural language responses
- [ ] CLI interface works smoothly
- [ ] Response time < 3 seconds
- [ ] Sources cited in answers
- [ ] Voice integration (Stage 2)
- [ ] Discord integration (Stage 3)

---

## Next Steps

1. Create project structure with uv
2. Install dependencies
3. Implement core components
4. Test and iterate
5. Plan Discord/voice integration

---

## Environment Setup Commands

```bash
# Install uv (if not already installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Initialize project (already done)
uv init

# Install dependencies (already done)
uv add click google-generativeai python-dotenv requests

# Create project structure (already done)
mkdir -p core interfaces api
```

## Running the Project

**Always use `uv run` to execute commands:**

```bash
# Ask questions
uv run main.py "Do I need cat figurine?"
uv run main.py "price of AK-74N"
uv run main.py "LEDX price"

# Or explicitly use ask command
uv run main.py ask "Do I need cat figurine?"

# Stage 2 (voice support)
uv run main.py --voice "Do I need cat figurine?"
uv run main.py --voice --no-speak "price of AK-74N"  # Voice input, text output
```

**Why use `uv run`?**
- Automatically activates the virtual environment
- Ensures correct Python interpreter and dependencies
- Handles environment variables from `.env` file
- Consistent execution across different systems

## Development Setup

### IDE Configuration (VS Code / Cursor)

**For Linter Errors:**
1. **Use `uv run` in terminal** - This ensures the virtual environment is active
2. **Configure Python Interpreter:**
   - Open Command Palette (`Ctrl+Shift+P`)
   - Select "Python: Select Interpreter"
   - Choose the interpreter from `.venv` directory
3. **Install Python extension** if linter errors persist

**Alternative: Use uv run for all development:**

```bash
# Run tests
uv run python tests/test_core.py

# Run with debugging
uv run python -m pdb main.py ask "test question"

# Install new dependencies
uv add new-package
```

### Environment Variables

Create a `.env` file in the project root:

```bash
# .env
GROQ_API_KEY=your_groq_api_key_here
DISCORD_BOT_TOKEN=your_discord_token_here  # For future use
GOOGLE_APPLICATION_CREDENTIALS=path/to/speech_credentials.json  # For future use
```

**The `.env` file is automatically loaded when using `uv run`.**

## Troubleshooting

### Linter Errors
If you see import errors in your IDE:
1. **Use `uv run`** for all Python commands
2. **Configure Python interpreter** in your IDE to use `.venv/bin/python`
3. **Restart your IDE** after changing interpreter settings
4. **Check dependencies** with `uv sync`

### Common Issues
- **Module not found**: Run `uv sync` to ensure dependencies are installed
- **API errors**: Check `.env` file has correct API keys
- **No item found**: Verify item name spelling against tarkov.dev

---

## API Setup

### Tarkov.dev API
- **Endpoint**: `https://api.tarkov.dev/graphql`
- **Method**: POST with JSON payload
- **No authentication required**
- **Rate limiting**: No official limits (be reasonable)

### Groq
1. Get API key from Groq Console
2. Set environment variable: `export GROQ_API_KEY=your_key`
3. Model: `openai/gpt-oss-20b` (free tier available)

### Google Speech-to-Text (Future)
1. Enable Google Cloud Speech-to-Text API
2. Create service account and download JSON key
3. Set environment variable: `export GOOGLE_APPLICATION_CREDENTIALS=path/to/key.json`

### Discord (Future)
1. Create Discord bot at Discord Developer Portal
2. Get bot token
3. Set environment variable: `export DISCORD_BOT_TOKEN=your_token`

---

## File Structure After Implementation

```
tarkbot/
├── core/
│   ├── __init__.py
│   ├── tarkov_api_client.py    # tarkov.dev GraphQL API wrapper
│   ├── item_lookup.py          # Item search and data processing
│   └── response_formatter.py   # Gemini-powered natural responses
├── interfaces/
│   ├── __init__.py
│   ├── cli_interface.py        # CLI commands (text input/output)
│   └── voice_interface.py      # Voice I/O (stage 2)
├── api/
│   ├── __init__.py
│   └── gemini_client.py        # Gemini API client
├── tests/
│   ├── test_core.py            # Core functionality tests
│   └── test_queries.py         # Sample query tests
├── main.py                     # CLI entry point
├── pyproject.toml              # Dependencies
└── .env                        # Environment variables
```

This plan provides a solid foundation for building the TarkBot AI agent with clear upgrade paths to Discord and voice functionality.
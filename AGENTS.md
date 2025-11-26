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
│   ├── response_formatter.py   # LLM-powered natural responses
├── interfaces/
│   ├── __init__.py
│   ├── cli_interface.py        # CLI commands (text input/output)
│   └── voice_interface.py      # Voice I/O
├── api/
│   ├── __init__.py
│   ├── groq_client.py          # Groq API client
│   └── tarkov_api_client.py    # tarkov.dev GraphQL API wrapper
├── main.py                     # Entry point
├── .env-example                # API keys template
└── config.toml                 # Keybind configuration
```

### Step 1.2: Dependencies ✅ UPDATED
**Choice**: Minimal dependencies focused on API integration and voice
```
click>=8.3.1
groq>=0.9.0
num2words>=0.5.13
numpy>=1.24.0
sounddevice>=0.4.6
soundfile>=0.12.0
python-dotenv>=1.2.1
requests>=2.32.5
pynput>=1.8.1
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

### Step 2.3: Data Structure ✅ IMPLEMENTED
**Choice**: API response format with natural language processing
```json
{
  "item_name": "Cat figurine",
  "flea_price": 39554,
  "quests": [
    {
      "quest_name": "Living High is Not a Crime - Part 1",
      "trader": "Ragman",
      "count": 1,
      "found_in_raid": true
    }
  ],
  "hideouts": [
    {
      "hideout_name": "Hall of Fame",
      "level": 1,
      "count": 1
    }
  ]
}
```

---

## Phase 3: Query Processing & LLM Integration

### Step 3.1: LLM Provider ✅ IMPLEMENTED
**Choice**: Groq with OpenAI GPT-OSS-20B
- Fast inference with Groq platform
- Advanced reasoning for item extraction and response formatting
- Generous free tier
- Access to OpenAI models via Groq

### Step 3.2: Query Classification ✅ IMPLEMENTED
**Choice**: Direct item extraction from natural language
- Extract item names from user questions
- Query tarkov.dev API for item data
- Filter for pricing and quest requirements
- Simple and efficient processing

### Step 3.3: Response Generation ✅ IMPLEMENTED
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

### Step 5.1: CLI Framework ✅ IMPLEMENTED
**Choice**: Click framework
- Professional CLI with commands, options, help
- Better user experience
- Command structure for development and testing

### Step 5.2: Command Structure ✅ IMPLEMENTED
**Choice**: Simple item inquiry commands
```bash
# Ask questions
uv run main.py ask "Do I need cat figurine?"

# Stage 2 (voice support)
uv run main.py ask --voice

# No arguments - defaults to voice mode
uv run main.py
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

## Implementation Order

1. Setup + Core API integration + Item lookup
2. Response formatting + CLI interface
3. Testing + Optimization
4. Voice integration

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
- **Groq-powered formatting** for natural responses
- **API caching** for performance optimization
- **Basic metrics** for response time tracking

---

## Success Criteria

- [x] Can provide vendor and flea market prices for items
- [x] Can identify quest requirements with FIR status
- [x] Provides natural language responses
- [x] CLI interface works smoothly
- [x] Response time < 3 seconds
- [x] Sources cited in answers
- [x] Voice integration
- [x] Configurable keybinds

---

## Current Implementation Status

### ✅ Completed Features
- **API Integration**: Full tarkov.dev GraphQL API integration with caching
- **Item Lookup**: Multi-word search matching with substring priority for improved accuracy
- **LLM Integration**: Groq GPT-OSS-20B for natural language processing
- **Voice Input**: Groq Whisper Large V3 Turbo for speech-to-text
- **Voice Output**: Groq PlayAI TTS with number-to-text conversion for proper pronunciation
- **CLI Interface**: Click-based CLI with text and voice modes, defaults to voice on no args
- **Response Formatting**: Natural language responses with pricing and quest info
- **Number Formatting**: TTS converts numbers to words while text output remains numerical
- **Config Support**: TOML config file for customizable keybinds with defaults
- **Windows Build**: Automated PyInstaller build with config files in release zip

### 🔄 Working Features
- Text queries with natural language item extraction
- Voice input with 5-second recording duration
- Interactive voice mode: Press 'Ctrl+`' to speak, 'Ctrl+Q' to quit
- Voice output with proper number pronunciation
- Debug mode for structured JSON output
- Test suite with sample queries
- Cross-platform keypress detection (no root/admin privileges required)
- Focus-independent input on Windows (works when window is unfocused)

### 📋 Next Steps
1. **Voice activity detection**: Optional - add VAD to reduce recording duration
2. **Error handling**: Improve API failure recovery and retry logic
3. **Performance**: Add response time metrics and optimization
4. **Documentation**: Final README and usage examples



---

## Next Steps

1. Create project structure with uv
2. Install dependencies
3. Implement core components
4. Test and iterate
5. Plan voice integration

---

## Environment Setup Commands

```bash
# Install uv (if not already installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Initialize project (already done)
uv init

# Install dependencies (already done)
uv sync

# Create project structure (already done)
mkdir -p core interfaces api
```

## Running the Project

**Always use `uv run` to execute commands:**

```bash
# Ask questions
uv run main.py ask "Do I need cat figurine?"

# Stage 2 (voice support)
uv run main.py ask --voice
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
uv run main.py test

# Run with debugging
uv run main.py test --debug

# Install new dependencies
uv add new-package
```

### Environment Variables

Create a `.env` file in the project root (copy from `.env-example`):

```bash
# .env
GROQ_API_KEY=your_groq_api_key_here
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
- **API errors**: Check `.env` file has correct Groq API key
- **No item found**: Verify item name spelling against tarkov.dev
- **Windows Defender warning**: The executable is unsigned; add to exclusions if needed

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



---

## File Structure After Implementation

```
tarkbot/
├── core/
│   ├── __init__.py
│   ├── response_formatter.py   # LLM-powered natural responses
├── interfaces/
│   ├── __init__.py
│   ├── cli_interface.py        # CLI commands (text input/output)
│   └── voice_interface.py      # Voice I/O
├── api/
│   ├── __init__.py
│   ├── groq_client.py          # Groq API client
│   └── tarkov_api_client.py    # tarkov.dev GraphQL API wrapper
├── main.py                     # Entry point
├── .env-example                # API keys template
└── config.toml                 # Keybind configuration
```

This plan provides a solid foundation for building the TarkBot AI agent with voice functionality.

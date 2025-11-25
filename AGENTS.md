# TarkBot AI Agent Implementation Plan

## Project Overview
Build an AI agent that answers Escape from Tarkov questions using the official wiki as source of truth, evolving from CLI to voice Discord bot.

---

## Phase 1: Project Setup & Core Infrastructure

### Step 1.1: Project Structure ✅ CONFIRMED
**Choice**: Option B (Modular structure for extensibility)
```
tarkbot/
├── core/
│   ├── __init__.py
│   ├── scraper.py
│   ├── embeddings.py
│   ├── vector_store.py
│   └── query_engine.py
├── interfaces/
│   ├── __init__.py
│   └── cli_interface.py
├── api/
│   ├── __init__.py
│   └── llm_client.py
├── data/
│   └── .gitkeep
├── main.py
└── requirements.txt
```

### Step 1.2: Dependencies ✅ CONFIRMED
**Choice**: Option B (Enhanced requirements for future voice support)
```
beautifulsoup4>=4.14.2
click>=8.3.1
discord-py>=2.6.4
google-generativeai>=0.8.5
openai>=2.8.1
pydub>=0.25.1
python-dotenv>=1.2.1
requests>=2.32.5
sentence-transformers>=5.1.2
```

### Step 1.3: Package Manager ✅ CONFIRMED
**Choice**: uv (Modern, fast, all-in-one Python package manager)

---

## Phase 2: Data Collection & Processing

### Step 2.1: Target Wiki Pages ✅ CONFIRMED
**Choice**: Option A (Essential pages with CLI management)
- Weapons, Ammunition, Armor
- Quests, Maps, Extract locations
- CLI commands for adding/removing categories

### Step 2.2: Scraping Strategy ✅ CONFIRMED
**Choice**: Option B (Batch scraping with caching)
- Scrape entire categories at once
- Local caching with update schedule
- Faster responses, offline capability
- Avoid unnecessary API hits

### Step 2.3: Data Structure ✅ CONFIRMED
**Choice**: Option B (Rich metadata)
```python
{
    "title": "AK-74N",
    "category": "weapons",
    "subcategory": "assault_rifles",
    "content": "Weapon description...",
    "metadata": {
        "caliber": "5.45x39mm",
        "ergonomics": 38,
        "recoil": 120,
        "slots": ["mod_scope", "mod_muzzle"]
    },
    "url": "https://...",
    "last_updated": "2024-01-01"
}
```

---

## Phase 3: Vector Storage & Search

### Step 3.1: Embedding Model ✅ CONFIRMED
**Choice**: Option B (`all-mpnet-base-v2`)
- Higher quality embeddings
- Better understanding of Tarkov terminology
- 768 dimensions, moderate speed

### Step 3.2: Chunking Strategy ✅ CONFIRMED
**Choice**: Option B (Semantic chunking)
- Respect section boundaries (headings, paragraphs)
- Maintain context integrity
- Variable chunk sizes based on content structure

### Step 3.3: Vector Store Configuration ✅ UPDATED
**Choice**: Option B (Persistent storage)
- Numpy-based vector store with local files (no ChromaDB dependency)
- Survives restarts, lightweight and fast
- Data persistence between sessions

---

## Phase 4: Query Processing & LLM Integration

### Step 4.1: LLM Provider ✅ CONFIRMED
**Choice**: Google Gemini 2.0 Flash-Lite
- Latest generation model
- Fast responses with good reasoning
- Free tier available
- Perfect balance of speed and quality

### Step 4.2: Query Classification ✅ CONFIRMED
**Choice**: Option C (Hybrid approach)
- Simple keyword rules for common patterns (80% of queries)
- LLM fallback for complex queries (20% of queries)
- Balance of speed and flexibility
- Natural language support

### Step 4.3: Response Generation ✅ CONFIRMED
**Choice**: Option C (Adaptive response)
- Simple queries: Direct retrieval (fast)
- Complex queries: RAG synthesis (detailed)
- Optimize for speed vs quality

---

## Phase 5: CLI Interface Development

### Step 5.1: CLI Framework ✅ CONFIRMED
**Choice**: Option B (Click framework)
- Professional CLI with commands, options, help
- Better user experience
- Command structure for development and testing

### Step 5.2: Command Structure ✅ CONFIRMED
**Choice**: Option C (Subcommands with default ask)
```bash
# Default command (ask)
python main.py "What is the best 7.62x39 ammo?"

# Category management
python main.py category add --name medical --url "https://..."
python main.py category remove --name medical
python main.py category list

# Data operations
python main.py data scrape --category weapons
python main.py data stats
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

1. **Week 1**: Setup + Core scraping + Vector store
2. **Week 2**: Query engine + CLI interface
3. **Week 3**: Testing + Optimization
4. **Week 4**: Discord bot (optional)
5. **Week 5**: Voice integration (optional)

---

## Key Technical Decisions

### Architecture
- **Modular design** for easy interface swapping
- **Separation of concerns** between core logic and interfaces
- **Unified response format** for all interfaces

### Data Management
- **Targeted scraping** with CLI category management
- **Rich metadata** for precise queries
- **Persistent caching** to avoid API calls
- **Semantic chunking** for context preservation

### Performance
- **Hybrid query classification** for speed
- **Adaptive response generation** for efficiency
- **Local embeddings** for fast retrieval
- **Basic metrics** for performance tracking

---

## Success Criteria

- [ ] Can answer basic ammo/weapon questions
- [ ] Handles map location queries
- [ ] Provides quest information
- [ ] CLI interface works smoothly
- [ ] Response time < 3 seconds
- [ ] Sources cited in answers
- [ ] Category management via CLI
- [ ] Persistent data storage

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
uv add requests beautifulsoup4 sentence-transformers openai click discord.py pydub python-dotenv google-generativeai

# Create project structure (already done)
mkdir -p core interfaces api data
```

## Running the Project

**Always use `uv run` to execute commands:**

```bash
# Ask questions (default behavior)
uv run main.py "What is the AK-74N?"

# Or explicitly use ask command
uv run main.py ask "What is the AK-74N?"

# Category management
uv run main.py category add --name medical --url "https://..."
uv run main.py category remove --name medical
uv run main.py category list

# Data operations
uv run main.py data scrape --category weapons
uv run main.py data stats
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
GEMINI_API_KEY=your_gemini_api_key_here
DISCORD_BOT_TOKEN=your_discord_token_here  # For future use
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
- **Vector store empty**: Run `uv run main.py scrape --category weapons` first

---

## API Setup

### Google Gemini
1. Get API key from Google AI Studio
2. Set environment variable: `export GEMINI_API_KEY=your_key`
3. Model: `gemini-2.0-flash-lite` (free tier available)

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
│   ├── scraper.py          # Wiki scraping logic
│   ├── embeddings.py       # Text processing
│   ├── vector_store.py     # Numpy-based vector storage
│   └── query_engine.py     # Core Q&A logic
├── interfaces/
│   ├── __init__.py
│   └── cli_interface.py    # CLI implementation
├── api/
│   ├── __init__.py
│   └── llm_client.py       # Gemini API client
├── data/
│   ├── vectors.npy         # Vector embeddings
│   ├── metadata.pkl        # Document metadata
│   ├── cache/              # Scraped content cache
│   └── categories.json     # Category configuration
├── tests/
│   ├── test_core.py        # Core functionality tests
│   └── test_queries.py     # Sample query tests
├── main.py                 # CLI entry point
├── requirements.txt        # Dependencies
└── .env                    # Environment variables
```

This plan provides a solid foundation for building the TarkBot AI agent with clear upgrade paths to Discord and voice functionality.
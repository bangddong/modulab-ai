# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a LangChain-based AI agent learning project focused on building multilingual RAG (Retrieval-Augmented Generation) systems and ReAct agents. The project demonstrates various patterns for tool calling, custom tools, and agent implementations using vector databases (ChromaDB) for document retrieval.

**Primary Language:** Python 3.12+
**Package Manager:** uv (modern Python package manager)
**Main Framework:** LangChain with support for OpenAI, HuggingFace, and Ollama models

## Development Commands

### Environment Setup
```bash
# Install dependencies
uv sync

# Activate virtual environment (if needed)
source .venv/bin/activate  # Unix/macOS
.venv\Scripts\activate     # Windows
```

### Running Notebooks
```bash
# Start Jupyter
jupyter notebook

# Convert notebook to Python script (for inspection)
jupyter nbconvert --to script <notebook_name>.ipynb --stdout
```

### Database and Vector Store
- ChromaDB persisted in `./chroma_db/` directory
- SQLite database: `etf_database.db` (from previous ETF project)
- Text data files: `./data/` (Korean and English markdown files for Tesla/Rivian)

## Architecture

### Core Components

**1. Vector Store Collections:**
- `db_korean_cosine_metadata`: Korean documents with metadata (main collection)
- `db_openai`: Multilingual collection using OpenAI embeddings
- `db_huggingface`: Multilingual collection using HuggingFace BGE-M3
- `db_ollama`: Multilingual collection using Ollama embeddings
- `eng_db_openai`: English-only document collection

**2. Embedding Models:**
- OpenAI: `text-embedding-3-small` (supports Korean)
- HuggingFace: `BAAI/bge-m3` (multilingual support)
- Ollama: `nomic-embed-text` (limited Korean support)

**3. LLM Models:**
- Primary: `gpt-4.1-mini` and `gpt-4.1-nano` via OpenAI
- Configurable via `init_chat_model()` for flexibility

### Key Patterns

**Tool Creation Methods:**
1. `@tool` decorator - Simplest method for basic tools
2. `StructuredTool.from_function()` - For existing functions with custom schemas
3. `.as_tool()` on Runnables - Convert chains to tools

**Agent Types:**
- LangChain `create_agent()` - Standard agent with built-in tool support
- ReAct agents - Reasoning and Acting pattern with observation loops

**RAG Strategies:**
1. **Cross-lingual search** - Single multilingual vector store
2. **Translation-based** - Detect language, translate to Korean, search, translate back
3. **Routing-based** - Detect language, route to language-specific vector store

### Document Processing Pipeline

```
Raw markdown → TextLoader → RecursiveCharacterTextSplitter
→ TikToken chunking (300 tokens, 50 overlap)
→ Embedding → ChromaDB
```

## Environment Variables

Required in `.env` file:
- `OPENAI_API_KEY` - OpenAI API access
- `LANGSMITH_TRACING`, `LANGSMITH_API_KEY`, `LANGSMITH_PROJECT` - LangSmith observability
- `TAVILY_API_KEY` - Web search tool
- `DEEPL_API_KEY` - Translation service
- `GOOGLE_API_KEY`, `PINECONE_API_KEY` - Optional services
- `LANGFUSE_*` - Langfuse tracing (alternative to LangSmith)

## Important Implementation Details

**Retriever Configuration:**
- Default k=4 for similarity search
- Use `search_kwargs={'k': n}` to customize result count
- MMR (Maximum Marginal Relevance) available for diversity

**Tool Return Behavior:**
- `return_direct=True` - Tool output goes directly to user
- `return_direct=False` - Tool output processed by LLM (default)

**Text Splitting:**
- Use regex separators: `['\n\n', '\n', r'(?<=[.!?])\s+']`
- TikToken encoding: `cl100k_base`
- Keep separators: `keep_separator=True`

**Language Detection:**
- Library: `langdetect`
- Usage: `detect(text)` returns language code ('ko', 'en', etc.)

**Cross-Encoder Reranking:**
- Model: `BAAI/bge-reranker-base` via HuggingFace
- Pattern: Retrieve k=10, rerank to top_n=3
- Use `ContextualCompressionRetriever` with `CrossEncoderReranker`

## Notebook Organization

- `PRJ03_W1_001_*` - Tool calling and agent fundamentals
- `PRJ03_W1_002_*` - Built-in tools (SQL, Tavily, Wikipedia)
- `PRJ03_W1_003_*` - Custom tools (Part 1: @tool, StructuredTool)
- `PRJ03_W1_004_*` - Custom tools (Part 2: Advanced patterns)
- `PRJ03_W1_005_*` - ReAct agents and multilingual RAG system

Each notebook contains:
- Concept explanation in markdown cells
- Implementation examples
- Practice exercises marked with `[실습]`

## Working with This Codebase

**When creating new tools:**
1. Define clear input schema using Pydantic models
2. Provide descriptive docstrings (LLM uses these for tool selection)
3. Consider both sync and async versions for performance
4. Test tool directly before binding to LLM

**When building RAG chains:**
1. Load appropriate vector store collection for language
2. Configure retriever with suitable k value
3. Use prompt templates that specify context usage rules
4. Include metadata formatting for source attribution

**When debugging agents:**
1. Use `stream_mode="values"` to observe intermediate steps
2. Check `tool_calls` attribute on AIMessage for tool selection
3. Verify tool schemas match LLM expectations
4. Review LangSmith traces for detailed execution flow

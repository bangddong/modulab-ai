# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is an ETF (Exchange-Traded Fund) recommendation system that uses AI/LLM to provide personalized investment recommendations. The system combines web crawling, Text2SQL, RAG (Retrieval-Augmented Generation), and LangGraph to analyze user investment profiles and recommend suitable ETFs from Korean markets.

## Core Architecture

### Multi-Agent Workflow (LangGraph)
The main application (`app.py`) implements a state machine with 5 sequential nodes:

1. **analyze_profile** - Extracts investment profile from natural language query using structured output
2. **write_query** - Generates SQL query based on user profile and ETF database schema
3. **execute_query** - Runs SQL query to fetch candidate ETFs
4. **rank_etfs** - Ranks candidates (1-3) based on composite scoring
5. **generate_explanation** - Creates markdown-formatted portfolio recommendation

State flows unidirectionally: START → analyze_profile → write_query → execute_query → rank_etfs → generate_explanation → END

### Database Structure
- **Database**: SQLite (`etf_database.db`)
- **Table**: `ETFs` - Primary ETF listings with 14 columns including:
  - 종목코드 (TEXT PRIMARY KEY) - 6-digit ETF ticker code
  - 종목명, 운용사, 기초지수 - Korean text fields
  - 수익률_최근1년, 총보수, 순자산총액 - Numeric performance metrics
  - Full schema in app.py:27-40

### Key Components

**Entity Retrieval (High-Cardinality Search)**
- Lines 32-65 in app.py
- Uses InMemoryVectorStore with OpenAI embeddings (text-embedding-3-large)
- Pre-indexes ETF names, fund managers, and underlying indices
- Retrieves top 20 similar entities via semantic search
- Critical for handling Korean proper noun variations in SQL generation

**Structured Output Models**
- `InvestmentProfile` (BaseModel) - User profile schema with enums for risk/horizon
- `QueryOutput` (TypedDict) - SQL query + Korean explanation
- `ETFRanking` (TypedDict) - Individual ETF ranking with score/reason
- `RecommendationExplanation` (BaseModel) - Final markdown output with `.to_markdown()` method

**Prompt Engineering**
- Query generation prompt includes: dialect, schema, entity_info (RAG), user_profile
- Ranking considers: 수익률, 변동성, 순자산총액, 총보수, profile matching
- Explanation template structures output into 4 sections: overview, recommendations table, ETF details, considerations

## Development Commands

### Running the Application
```bash
# Install dependencies
pip install -r requirements.txt

# Set up environment variables (required)
# Create .env file with OPENAI_API_KEY=your_key

# Run Gradio interface
python app.py

# Access at http://localhost:7860
```

### Working with Notebooks
The repository contains educational notebooks organized by week:
- Week 1 (W1): RAG evaluation, retrieval metrics, keyword/hybrid search, reranking
- Week 2 (W2): LLM providers, generation metrics, LLM-as-Judge, Langfuse evaluation
- Week 3 (W3): ETF data collection (crawl4ai), Text2SQL, cardinality handling, recommendation system

To run notebooks:
```bash
jupyter notebook  # or use VSCode Jupyter extension
```

### Database Operations
```python
# Query database via Python
import sqlite3
conn = sqlite3.connect('etf_database.db')
cursor = conn.cursor()
cursor.execute("SELECT * FROM ETFs LIMIT 5")

# Or use LangChain's SQLDatabase
from langchain_community.utilities import SQLDatabase
db = SQLDatabase.from_uri("sqlite:///etf_database.db")
print(db.get_table_info())
```

## Important Implementation Details

### Text2SQL Pipeline
- Uses `create_retriever_tool` to inject entity context into query generation prompts
- Handles Korean character encoding (CSV files use `encoding='cp949'`)
- Implements cardinality awareness via semantic search to avoid exact string matching failures
- SQL queries sanitized via regex extraction (see notebooks for `extract_sql()` pattern)

### Gradio Interface Configuration
- Type: "messages" (chat interface with history)
- Input processing: Stateless - history parameter unused in `answer_invoke()`
- Error handling: Returns markdown-formatted error messages on exceptions
- Example prompts provided for user guidance (age, amount, preferences, ESG)

### LLM Model Usage
- Primary: GPT-4.1-mini for profile/ranking/explanation (app.py:125, 194, 258)
- Structured output: `.with_structured_output()` enforces Pydantic schemas
- Note: Some notebooks compare GPT vs Gemini models - only GPT used in production app

### Data Collection (Crawl4AI)
Notebooks show web scraping patterns for ETF details:
- Uses AsyncWebCrawler with BrowserConfig (headless chromium)
- Handles dynamic content via `wait_for` and `js_code` options
- Extraction strategies: JsonCssExtractionStrategy or LLMExtractionStrategy
- Windows async: Requires WindowsProactorEventLoopPolicy + nest_asyncio

## Critical Constraints

**Korean Language Processing**
- All user-facing text must be in Korean (한국어)
- CSV encoding: Always use `encoding='cp949'` for Korean market data
- Database fields use Korean column names - do not translate in queries
- Markdown output formatting preserves Korean characters

**LangGraph State Management**
- State is TypedDict - cannot add arbitrary keys
- All nodes must return dict with valid State keys
- State flows are immutable - use return values to update
- No cycles in current graph implementation

**Database Schema**
- 종목코드 is TEXT not INTEGER despite being 6 digits (leading zeros matter)
- Numeric fields (수익률, 총보수) can be NULL - handle with pd.notna() checks
- Date field (상장일) stored as TEXT in YYYY/MM/DD format
- Never use SELECT * - explicitly list columns per QUERY_TEMPLATE guidelines

## Testing Patterns

When modifying the recommendation system:
1. Test with Korean investment queries matching the example format
2. Verify SQL query validity via `db.run()` before LLM integration
3. Check entity retrieval with `entity_retriever_tool.invoke(question)`
4. Validate structured outputs match Pydantic schemas
5. Confirm markdown rendering in Gradio interface

## File Organization

- `app.py` - Production Gradio application (main entry point)
- `etf_database.db` - SQLite database with ETF data
- `data/` - CSV files for ETF listings and scraped details
- `PRJ02_W3_*.ipynb` - Week 3 notebooks showing pipeline development stages
- `requirements.txt` - Python dependencies (gradio, langchain, langgraph, etc.)
- `.env` - Environment variables (not in repo - create locally with OPENAI_API_KEY)

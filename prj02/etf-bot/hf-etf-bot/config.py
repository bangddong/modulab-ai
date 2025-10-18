"""
Configuration file for ETF Recommendation System
"""

# LLM Configuration
DEFAULT_MODEL = "gpt-4o-mini"
EMBEDDING_MODEL = "text-embedding-3-large"
TEMPERATURE = 0

# Query Configuration
MAX_RETRY_COUNT = 3
TOP_K_CANDIDATES = 15
TOP_N_RECOMMENDATIONS = 3

# RAG Configuration
ENTITY_RETRIEVAL_K = 20

# Database Configuration
DATABASE_URI = "sqlite:///etf_database.db"

# Gradio Configuration
SERVER_NAME = "0.0.0.0"
SERVER_PORT = 7860
SHARE = False

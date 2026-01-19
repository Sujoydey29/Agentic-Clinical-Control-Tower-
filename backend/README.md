# ACCT Backend - Agentic Clinical Control Tower

A FastAPI backend for the Agentic Clinical Control Tower (ACCT) system.

## Tech Stack
- **Framework**: FastAPI
- **Database**: Supabase (PostgreSQL + pgvector)
- **LLM**: Ollama Llama 3.2:1b (Local)
- **Embeddings**: all-MiniLM-L6-v2 (Local)
- **Package Manager**: uv

## Setup

```bash
# Activate virtual environment
uv sync

# Run development server
uv run uvicorn app.main:app --reload --port 8000
```

## Project Structure
```
backend/
├── app/
│   ├── api/          # API route handlers
│   ├── core/         # Configuration, database, settings
│   ├── models/       # Pydantic models & SQLAlchemy schemas
│   ├── services/     # Business logic services
│   ├── agents/       # LangGraph agentic workflows
│   └── main.py       # FastAPI application entry
├── pyproject.toml    # Project dependencies
└── .env              # Environment variables
```

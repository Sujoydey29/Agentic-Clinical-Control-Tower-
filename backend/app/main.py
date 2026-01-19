"""
ACCT Backend - Main FastAPI Application
Agentic Clinical Control Tower
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from datetime import datetime

from .core import get_settings
from .api import patients, forecasts, ml, timeseries, nlp, rag, agents, communication, evaluation


settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    # Startup
    print("🚀 ACCT Backend starting up...")
    print(f"   Ollama Model: {settings.ollama_model}")
    print(f"   Debug Mode: {settings.debug}")
    yield
    # Shutdown
    print("👋 ACCT Backend shutting down...")


app = FastAPI(
    title="ACCT Backend",
    description="Agentic Clinical Control Tower - AI-powered hospital operations management",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS middleware for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],  # Next.js dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(patients.router, prefix="/api/v1")
app.include_router(forecasts.router, prefix="/api/v1")
app.include_router(ml.router, prefix="/api/v1")
app.include_router(timeseries.router, prefix="/api/v1")
app.include_router(nlp.router, prefix="/api/v1")
app.include_router(rag.router, prefix="/api/v1")
app.include_router(agents.router, prefix="/api/v1")
app.include_router(communication.router, prefix="/api/v1")
app.include_router(evaluation.router, prefix="/api/v1")


@app.get("/")
async def root():
    """Root endpoint - API info."""
    return {
        "name": "ACCT Backend",
        "version": "0.1.0",
        "status": "operational",
        "timestamp": datetime.utcnow().isoformat(),
        "docs": "/docs",
    }


@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring."""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "components": {
            "api": "up",
            "database": "mock",  # Will be "up" when Supabase is connected
            "ollama": "pending",  # Will check connection
        }
    }


@app.get("/api/v1/status")
async def api_status():
    """API status with feature availability."""
    return {
        "version": "v1",
        "features": {
            "patients": True,
            "forecasts": True,
            "agents": False,  # Coming in Part 6
            "rag": False,  # Coming in Part 5
        },
        "llm": {
            "provider": "ollama",
            "model": settings.ollama_model,
            "status": "configured",
        }
    }

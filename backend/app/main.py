"""
Prompt Trainer - FastAPI Application

This is the main entry point for the backend API.
FastAPI automatically generates interactive API docs at /docs

Tech Tip: FastAPI is "async-first" which means it can handle
multiple requests simultaneously without blocking.
"""

from contextlib import asynccontextmanager
from datetime import datetime, timezone
import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.database import init_db
from app.core.config import get_settings
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

@asynccontextmanager
async def lifespan(_app: FastAPI):
    """Lifecycle manager to handle startup/shutdown without deprecated hooks."""
    init_db()
    print(">> Prompt Trainer API started")
    print(">> API Documentation: http://localhost:8000/docs")
    yield
    print(">> Prompt Trainer API shutting down")


# Initialize FastAPI application
app = FastAPI(
    title="Prompt Trainer API",
    description="AI-powered paper grading system that learns from user feedback",
    version="0.1.0",
    docs_url="/docs",  # Swagger UI at http://localhost:8000/docs
    redoc_url="/redoc",  # Alternative docs at http://localhost:8000/redoc
    lifespan=lifespan,
)

# CORS Configuration
# Tech Tip: CORS (Cross-Origin Resource Sharing) allows your frontend
# (running on port 5173) to make requests to your backend (port 8000).
# Without this, browsers block the requests for security.
allowed_origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:5173").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,  # Frontend URLs
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods (GET, POST, PUT, DELETE, etc.)
    allow_headers=["*"],  # Allow all headers
)


# Root endpoint - health check
@app.get("/", tags=["Health"])
async def root():
    """
    Health check endpoint.

    Returns basic API information.
    Useful for monitoring if the API is running.
    """
    return {
        "message": "Prompt Trainer API",
        "status": "running",
        "version": "0.1.0",
        "docs": "/docs"
    }


# Health check endpoint
@app.get("/health", tags=["Health"])
async def health_check():
    """
    Detailed health check.

    Future: Add database connection check, Ollama status, etc.
    """
    settings = get_settings()
    return {
        "status": "healthy",
        "database": "connected",
        "adapter": "ollama" if settings.ollama_enabled else "stub",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }


# Include API routers
from app.api import papers, rubrics, evaluations

# Papers API - CRUD operations for submitted papers
app.include_router(papers.router, prefix="/api/papers", tags=["Papers"])

# Rubrics API - Grading rubrics with criteria
app.include_router(rubrics.router, prefix="/api/rubrics", tags=["Rubrics"])

# Evaluations API - Stubbed evaluation creation
app.include_router(evaluations.router, prefix="/api/evaluations", tags=["Evaluations"])

# Future routers:
# from app.api import evaluations, prompts
# app.include_router(evaluations.router, prefix="/api/evaluations", tags=["Evaluations"])
# app.include_router(prompts.router, prefix="/api/prompts", tags=["Prompts"])


# Tech Tip: How to run this application
#
# Development (with auto-reload):
#   uvicorn app.main:app --reload
#
# Production:
#   uvicorn app.main:app --host 0.0.0.0 --port 8000
#
# The API will be available at:
#   http://localhost:8000
#
# Interactive docs at:
#   http://localhost:8000/docs

"""
Main application entry point for web UI.

This extends the original src/main.py with authentication and dashboard endpoints.
"""
from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

# Import original app creation
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.main import create_app as create_original_app

# Import new modules
from backend.api.auth import router as auth_router
from backend.api.dashboard import router as dashboard_router
from backend.database import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    # Startup
    init_db()  # Initialize database tables
    yield
    # Shutdown
    pass


def create_web_app() -> FastAPI:
    """
    Create FastAPI application with web UI support.

    Extends the original app with:
    - Authentication endpoints
    - Dashboard API
    - Static file serving for frontend
    - CORS middleware
    """
    # Create original app (with webhook and healthz endpoints)
    app = create_original_app()

    # Update app metadata
    app.title = "Feishu HR Translator - Web UI"
    app.description = "AI-powered HR report translation with web interface"
    app.version = "2.0.0"

    # Add CORS middleware for frontend development
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://localhost:3000",  # React dev server
            "http://localhost:3001",  # Vite dev server (alternative port)
            "http://localhost:5173",  # Vite dev server
            "http://127.0.0.1:3000",
            "http://127.0.0.1:3001",
            "http://127.0.0.1:5173",
        ],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Include new routers
    app.include_router(auth_router)
    app.include_router(dashboard_router)

    # Serve static files (frontend build) in production
    # Uncomment this after building frontend:
    # app.mount("/", StaticFiles(directory="frontend/dist", html=True), name="static")

    return app


app = create_web_app()

# Initialize database on startup
init_db()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "web_main:app",
        host="0.0.0.0",
        port=8080,
        reload=True,  # Enable auto-reload during development
    )

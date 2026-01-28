"""FastAPI application factory and static file serving."""

from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from api.routes import config, health, models, processing

FRONTEND_DIR = Path(__file__).parent.parent / "frontend" / "dist"


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    app = FastAPI(
        title="Docling Playground",
        description="Interactive document processing playground",
        version="0.1.0",
    )

    # Register API routes
    app.include_router(health.router)
    app.include_router(config.router)
    app.include_router(processing.router)
    app.include_router(models.router)

    # Serve React SPA static files (mount AFTER API routes)
    if FRONTEND_DIR.exists():
        app.mount(
            "/",
            StaticFiles(directory=str(FRONTEND_DIR), html=True),
            name="frontend",
        )

    return app


app = create_app()

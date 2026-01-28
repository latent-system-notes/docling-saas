"""Health check endpoint."""

from fastapi import APIRouter

router = APIRouter(prefix="/api", tags=["health"])


@router.get("/health")
async def health_check():
    """Return service health status."""
    from src.model_manager import ModelManager

    manager = ModelManager()
    return {
        "status": "healthy",
        "version": "0.1.0",
        "offline_mode": manager.is_offline_mode(),
    }

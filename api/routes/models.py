"""Model management endpoints."""

import asyncio

from fastapi import APIRouter, Depends, HTTPException

from api.dependencies import get_model_manager
from src.model_manager import ModelManager
from src.models import ModelStatus

router = APIRouter(prefix="/api/models", tags=["models"])


@router.get("", response_model=list[ModelStatus])
async def list_models(
    manager: ModelManager = Depends(get_model_manager),
):
    """Get status of all models."""
    return await asyncio.to_thread(manager.get_model_status)


@router.post("/{model_id}/download")
async def download_model(
    model_id: str,
    manager: ModelManager = Depends(get_model_manager),
):
    """Download a specific model by ID."""
    messages: list[str] = []

    def progress_cb(msg: str):
        messages.append(msg)

    success = await asyncio.to_thread(manager.download_model, model_id, progress_cb)
    return {"success": success, "message": "; ".join(messages) if messages else None}


@router.post("/download-required")
async def download_required_models(
    manager: ModelManager = Depends(get_model_manager),
):
    """Download all required models."""
    messages: list[str] = []

    def progress_cb(msg: str):
        messages.append(msg)

    results = await asyncio.to_thread(manager.download_required, progress_cb)
    return results


@router.post("/download-all")
async def download_all_models(
    manager: ModelManager = Depends(get_model_manager),
):
    """Download all models including optional ones."""
    messages: list[str] = []

    def progress_cb(msg: str):
        messages.append(msg)

    results = await asyncio.to_thread(
        manager.download_all, True, progress_cb
    )
    return results


@router.delete("/cache")
async def clear_cache(
    manager: ModelManager = Depends(get_model_manager),
):
    """Clear the model cache directory."""
    success = await asyncio.to_thread(manager.clear_cache)
    return {"success": success}


@router.get("/disk-usage")
async def get_disk_usage(
    manager: ModelManager = Depends(get_model_manager),
):
    """Get disk usage of models directory."""
    usage = await asyncio.to_thread(manager.get_disk_usage)
    return usage

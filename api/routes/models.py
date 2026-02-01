"""Model management endpoints."""

import asyncio
import logging

from fastapi import APIRouter, Depends, HTTPException

from api.dependencies import get_model_manager
from src.config import disable_offline_mode, enable_offline_mode, get_offline_status
from src.model_manager import ModelManager
from src.models import ModelStatus

logger = logging.getLogger("docling-playground.api.models")
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
    disable_offline_mode()
    messages: list[str] = []

    def progress_cb(msg: str):
        messages.append(msg)

    try:
        success = await asyncio.to_thread(manager.download_model, model_id, progress_cb)
        return {"success": success, "message": "; ".join(messages) if messages else None}
    finally:
        enable_offline_mode()


@router.post("/download-required")
async def download_required_models(
    manager: ModelManager = Depends(get_model_manager),
):
    """Download all required models."""
    disable_offline_mode()
    messages: list[str] = []

    def progress_cb(msg: str):
        messages.append(msg)

    try:
        results = await asyncio.to_thread(manager.download_required, progress_cb)
        return results
    finally:
        enable_offline_mode()


@router.post("/download-all")
async def download_all_models(
    manager: ModelManager = Depends(get_model_manager),
):
    """Download all models including optional ones."""
    disable_offline_mode()
    messages: list[str] = []

    def progress_cb(msg: str):
        messages.append(msg)

    try:
        results = await asyncio.to_thread(
            manager.download_all, True, progress_cb
        )
        return results
    finally:
        enable_offline_mode()


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


@router.get("/offline-status")
async def get_offline_status_endpoint():
    """Get current offline mode status and configuration."""
    return get_offline_status()


@router.post("/download-easyocr")
async def download_easyocr_models(
    languages: list[str] = ["en", "ar"],
    manager: ModelManager = Depends(get_model_manager),
):
    """Download EasyOCR models for specified languages."""
    disable_offline_mode()
    messages: list[str] = []

    def progress_cb(msg: str):
        logger.info(msg)
        messages.append(msg)

    try:
        logger.info(f"Downloading EasyOCR models for languages: {languages}")
        success = await asyncio.to_thread(manager.download_easyocr_model, languages, progress_cb)
        return {"success": success, "languages": languages, "messages": messages}
    finally:
        enable_offline_mode()


@router.post("/verify-rapidocr")
async def verify_rapidocr_models(
    manager: ModelManager = Depends(get_model_manager),
):
    """Verify RapidOCR models are available."""
    messages: list[str] = []

    def progress_cb(msg: str):
        logger.info(msg)
        messages.append(msg)

    success = await asyncio.to_thread(manager.download_rapidocr_models, progress_cb)
    return {"success": success, "messages": messages}

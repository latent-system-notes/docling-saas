"""Singleton dependencies for FastAPI."""

from functools import lru_cache

from src.model_manager import ModelManager
from src.processor import DocumentProcessor


@lru_cache()
def get_processor() -> DocumentProcessor:
    """Get singleton DocumentProcessor instance."""
    return DocumentProcessor()


@lru_cache()
def get_model_manager() -> ModelManager:
    """Get singleton ModelManager instance."""
    return ModelManager()

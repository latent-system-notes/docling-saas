"""Configuration and constants for Docling Playground."""

import logging
import os
from enum import Enum
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="[%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("docling-playground")

# Project root directory
PROJECT_ROOT = Path(__file__).parent.parent.resolve()

# Local models directory (inside project)
MODELS_DIR = PROJECT_ROOT / "models"
HUGGINGFACE_MODELS_DIR = MODELS_DIR / "huggingface"
EASYOCR_MODELS_DIR = MODELS_DIR / "easyocr"
RAPIDOCR_MODELS_DIR = MODELS_DIR / "rapidocr"


def setup_model_directories():
    """Set up model directories and cache paths (but not offline mode)."""
    # Create directories if they don't exist
    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    HUGGINGFACE_MODELS_DIR.mkdir(parents=True, exist_ok=True)
    EASYOCR_MODELS_DIR.mkdir(parents=True, exist_ok=True)

    # Set HuggingFace cache to local models directory
    os.environ["HF_HOME"] = str(HUGGINGFACE_MODELS_DIR)
    os.environ["HF_HUB_CACHE"] = str(HUGGINGFACE_MODELS_DIR / "hub")

    # Remove deprecated TRANSFORMERS_CACHE if set - it can point to
    # a non-existent directory and break offline model resolution.
    # Modern transformers uses HF_HOME / HF_HUB_CACHE instead.
    os.environ.pop("TRANSFORMERS_CACHE", None)

    # Set EasyOCR model storage
    os.environ["EASYOCR_MODULE_PATH"] = str(EASYOCR_MODELS_DIR)

    logger.debug(f"Models directory: {MODELS_DIR}")
    logger.debug(f"HF_HOME: {os.environ.get('HF_HOME')}")
    logger.debug(f"EASYOCR_MODULE_PATH: {os.environ.get('EASYOCR_MODULE_PATH')}")


def enable_offline_mode():
    """Enable offline mode - no downloads allowed."""
    os.environ["HF_HUB_OFFLINE"] = "1"
    os.environ["TRANSFORMERS_OFFLINE"] = "1"
    logger.info("Offline mode ENABLED - models will be loaded from local cache only")


def disable_offline_mode():
    """Disable offline mode - allow downloads."""
    os.environ["HF_HUB_OFFLINE"] = "0"
    os.environ["TRANSFORMERS_OFFLINE"] = "0"
    logger.info("Offline mode DISABLED - downloads are now allowed")


def is_offline_mode() -> bool:
    """Check if offline mode is enabled."""
    return os.environ.get("HF_HUB_OFFLINE") == "1"


def get_offline_status() -> dict:
    """Get detailed offline mode status."""
    return {
        "offline_mode": is_offline_mode(),
        "hf_hub_offline": os.environ.get("HF_HUB_OFFLINE", "0"),
        "transformers_offline": os.environ.get("TRANSFORMERS_OFFLINE", "0"),
        "hf_home": os.environ.get("HF_HOME", "not set"),
        "easyocr_module_path": os.environ.get("EASYOCR_MODULE_PATH", "not set"),
        "models_dir": str(MODELS_DIR),
    }


# Auto-setup model directories on import (but don't set offline mode yet)
setup_model_directories()


class Accelerator(str, Enum):
    """Supported accelerator types."""
    AUTO = "auto"
    CPU = "cpu"
    CUDA = "cuda"
    MPS = "mps"


class PipelineType(str, Enum):
    """Pipeline types for document processing."""
    STANDARD = "standard"
    VLM = "vlm"


class OCRLibrary(str, Enum):
    """Supported OCR libraries."""
    RAPIDOCR = "rapidocr"
    EASYOCR = "easyocr"
    TESSERACT = "tesseract"


class OutputFormat(str, Enum):
    """Output format options."""
    JSON = "json"
    MARKDOWN = "markdown"
    SUMMARY = "summary"


# Default artifacts path
DEFAULT_ARTIFACTS_PATH = os.environ.get(
    "DOCLING_SERVE_ARTIFACTS_PATH",
    os.path.expanduser("~/.cache/docling/models")
)

# Supported file extensions
SUPPORTED_FILE_EXTENSIONS = [
    ".pdf", ".docx", ".pptx", ".html", ".htm",
    ".png", ".jpg", ".jpeg", ".tiff", ".tif", ".bmp"
]

# OCR language options per library
OCR_LANGUAGES = {
    OCRLibrary.RAPIDOCR: ["en", "ch", "japan", "korean", "german", "french"],
    OCRLibrary.EASYOCR: [
        "en", "ar", "zh_sim", "zh_tra", "ja", "ko",
        "fr", "de", "es", "ru", "pt", "it", "nl", "pl", "tr", "vi", "th"
    ],
    OCRLibrary.TESSERACT: [
        "eng", "ara", "chi_sim", "chi_tra", "jpn", "kor",
        "fra", "deu", "spa", "rus", "por", "ita", "nld", "pol", "tur"
    ],
}

# Default language mappings (normalized to library-specific codes)
DEFAULT_OCR_LANGUAGE = {
    OCRLibrary.RAPIDOCR: "en",
    OCRLibrary.EASYOCR: "en",
    OCRLibrary.TESSERACT: "eng",
}

# Model information for model management
MODELS_INFO = {
    "layout": {
        "name": "Layout (Heron)",
        "description": "Layout analysis for page structure detection",
        "size_mb": 164,
        "required": True,
        "hf_repo": "docling-project/docling-layout-heron",
        "subfolder": None,
    },
    "docling_models": {
        "name": "Docling Models",
        "description": "Core docling models (tableformer, picture classifier, etc.)",
        "size_mb": 342,
        "required": True,
        "hf_repo": "docling-project/docling-models",
        "subfolder": None,
    },
    "granite_docling_vlm": {
        "name": "GraniteDocling VLM",
        "description": "Vision-Language Model for document understanding",
        "size_mb": 4800,
        "required": False,
        "hf_repo": "ibm-granite/granite-vision-3.1-2b-preview",
        "subfolder": None,
    },
    "chunker_tokenizer": {
        "name": "Chunker Tokenizer (BGE)",
        "description": "Tokenizer used by HybridChunker for document chunking",
        "size_mb": 1,
        "required": True,
        "hf_repo": "BAAI/bge-small-en-v1.5",
        "subfolder": None,
    },
    "easyocr_en": {
        "name": "EasyOCR (en)",
        "description": "EasyOCR English model",
        "size_mb": 85,
        "required": False,
        "hf_repo": None,
        "ocr_library": OCRLibrary.EASYOCR,
        "language": "en",
    },
    "easyocr_ar": {
        "name": "EasyOCR (ar)",
        "description": "EasyOCR Arabic model",
        "size_mb": 120,
        "required": False,
        "hf_repo": None,
        "ocr_library": OCRLibrary.EASYOCR,
        "language": "ar",
    },
    "rapidocr": {
        "name": "RapidOCR",
        "description": "RapidOCR ONNX model",
        "size_mb": 12,
        "required": False,
        "hf_repo": None,
        "ocr_library": OCRLibrary.RAPIDOCR,
    },
}

# Default processing options
DEFAULT_OPTIONS = {
    "pipeline": PipelineType.STANDARD,
    "accelerator": Accelerator.AUTO,
    "ocr_enabled": True,
    "ocr_library": OCRLibrary.EASYOCR,
    "ocr_languages": ["en"],
    "force_full_page_ocr": False,
    "do_table_structure": True,
    "do_code_enrichment": False,
    "do_formula_enrichment": False,
    "do_picture_description": False,
    "output_format": OutputFormat.MARKDOWN,
    "chunk_max_tokens": 512,
}

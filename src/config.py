"""Configuration and constants for Docling Playground."""

import os
from enum import Enum
from pathlib import Path

# Project root directory
PROJECT_ROOT = Path(__file__).parent.parent.resolve()

# Local models directory (inside project)
MODELS_DIR = PROJECT_ROOT / "models"
HUGGINGFACE_MODELS_DIR = MODELS_DIR / "huggingface"
EASYOCR_MODELS_DIR = MODELS_DIR / "easyocr"
RAPIDOCR_MODELS_DIR = MODELS_DIR / "rapidocr"


def setup_offline_environment():
    """Set up environment variables to use local models directory and enable offline mode."""
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

    # Always enable offline mode - no downloads allowed
    os.environ["HF_HUB_OFFLINE"] = "1"
    os.environ["TRANSFORMERS_OFFLINE"] = "1"


# Auto-setup offline environment on import
setup_offline_environment()


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

# Server configuration
DEFAULT_SERVER_PORT = 7860
DEFAULT_SERVER_HOST = "0.0.0.0"

"""Configuration endpoint exposing enums, defaults, and language mappings."""

from fastapi import APIRouter

from src.config import (
    DEFAULT_OPTIONS,
    OCR_LANGUAGES,
    SUPPORTED_FILE_EXTENSIONS,
    Accelerator,
    OCRLibrary,
    OutputFormat,
    PipelineType,
)

router = APIRouter(prefix="/api", tags=["config"])


def _enum_options(enum_cls, labels: dict[str, str] | None = None):
    """Convert an enum to a list of {value, label} dicts."""
    result = []
    for member in enum_cls:
        label = labels.get(member.value, member.value.replace("_", " ").title()) if labels else member.value.replace("_", " ").title()
        result.append({"value": member.value, "label": label})
    return result


@router.get("/config")
async def get_config():
    """Return all configuration enums, defaults, and language mappings."""
    pipeline_labels = {"standard": "Standard", "vlm": "VLM"}
    accelerator_labels = {"auto": "Auto", "cpu": "CPU", "cuda": "CUDA", "mps": "MPS"}
    ocr_labels = {"rapidocr": "RapidOCR", "easyocr": "EasyOCR", "tesseract": "Tesseract"}
    format_labels = {"json": "JSON", "markdown": "Markdown", "summary": "Summary"}

    ocr_languages = {}
    for lib in OCRLibrary:
        ocr_languages[lib.value] = OCR_LANGUAGES.get(lib, [])

    defaults = {}
    for key, value in DEFAULT_OPTIONS.items():
        if hasattr(value, "value"):
            defaults[key] = value.value
        else:
            defaults[key] = value

    return {
        "pipelines": _enum_options(PipelineType, pipeline_labels),
        "accelerators": _enum_options(Accelerator, accelerator_labels),
        "ocr_libraries": _enum_options(OCRLibrary, ocr_labels),
        "ocr_languages": ocr_languages,
        "output_formats": _enum_options(OutputFormat, format_labels),
        "supported_extensions": SUPPORTED_FILE_EXTENSIONS,
        "defaults": defaults,
    }

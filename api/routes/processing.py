"""Document processing endpoint."""

import asyncio
import json

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile

from api.dependencies import get_processor
from src.models import ProcessingOptions, ProcessingResult
from src.processor import DocumentProcessor

router = APIRouter(prefix="/api", tags=["processing"])


@router.post("/process", response_model=ProcessingResult)
async def process_document(
    file: UploadFile = File(...),
    options: str = Form(default="{}"),
    processor: DocumentProcessor = Depends(get_processor),
):
    """Process an uploaded document.

    Accepts a multipart form with:
    - file: The document file to process
    - options: JSON string of ProcessingOptions
    """
    try:
        parsed_options = ProcessingOptions(**json.loads(options))
    except (json.JSONDecodeError, Exception) as e:
        raise HTTPException(status_code=422, detail=f"Invalid options: {e}")

    if not file.filename:
        raise HTTPException(status_code=400, detail="No filename provided")

    content = await file.read()

    result = await asyncio.to_thread(
        processor.process_bytes, content, file.filename, parsed_options
    )

    return result

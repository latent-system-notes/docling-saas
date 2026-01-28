# Blueprint: Docling Document Processing Service

> **Instructions for Claude Code**: This is a complete blueprint for building a document processing HTTP service. Follow the implementation steps in order. Create each file with the exact content provided.

---

## Project Overview

**Name**: `docling-service`
**Purpose**: HTTP microservice that accepts documents (PDF, HTML, URL, DOCX, images), processes them with Docling, and returns DoclingDocument + Chunks in multiple formats.

**Tech Stack**:
- FastAPI (HTTP framework)
- Docling (document processing)
- HybridChunker (text chunking)
- Pydantic (data validation)

---

## Project Structure

```
docling-service/
├── pyproject.toml
├── README.md
├── src/
│   ├── __init__.py
│   ├── main.py          # FastAPI app + endpoints
│   ├── config.py        # Settings and constants
│   ├── models.py        # Pydantic request/response models
│   ├── processor.py     # Core Docling processing logic
│   └── chunker.py       # HybridChunker wrapper
```

---

## Implementation Steps

### Step 1: Create `pyproject.toml`

```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["src"]

[project]
name = "docling-service"
version = "0.1.0"
description = "Document processing HTTP service using Docling"
requires-python = ">=3.11"
dependencies = [
    "fastapi>=0.115",
    "uvicorn>=0.32",
    "python-multipart>=0.0.9",
    "docling>=2.70",
    "transformers>=4.40",
    "pydantic>=2.0",
    "langdetect>=1.0.9",
]

[project.scripts]
docling-service = "src.main:run"
```

---

### Step 2: Create `src/__init__.py`

```python
"""Docling Document Processing Service."""
```

---

### Step 3: Create `src/config.py`

```python
"""Configuration and constants."""
import os
from pathlib import Path

# Chunking settings
MAX_TOKENS = 512
CHUNK_OVERLAP = 50

# Model settings (for tokenizer)
TOKENIZER_MODEL = "sentence-transformers/paraphrase-multilingual-mpnet-base-v2"

# OCR settings
OCR_LANGUAGES = ["english", "arabic"]
FORCE_FULL_PAGE_OCR = True

# Server settings
HOST = os.environ.get("HOST", "0.0.0.0")
PORT = int(os.environ.get("PORT", "8000"))

# Temp directory for uploads
TEMP_DIR = Path(os.environ.get("TEMP_DIR", "/tmp/docling-service"))
TEMP_DIR.mkdir(parents=True, exist_ok=True)
```

---

### Step 4: Create `src/models.py`

```python
"""Pydantic models for request/response."""
from datetime import datetime
from typing import Any
from pydantic import BaseModel, Field
from enum import Enum


class OutputFormat(str, Enum):
    JSON = "json"
    MARKDOWN = "markdown"
    SUMMARY = "summary"


class DocumentMetadata(BaseModel):
    """Metadata about the processed document."""
    filename: str
    file_type: str
    page_count: int | None = None
    language: str = "unknown"
    processed_at: datetime = Field(default_factory=datetime.now)


class ChunkOutput(BaseModel):
    """Single chunk output."""
    index: int
    text: str
    page_num: int | None = None
    token_count: int = 0
    preview: str | None = None  # For summary format


class ProcessingStats(BaseModel):
    """Statistics for summary output."""
    total_chunks: int
    total_tokens: int
    pages_processed: int | None


class ProcessingResult(BaseModel):
    """Response model for document processing."""
    success: bool
    error: str | None = None
    metadata: DocumentMetadata | None = None
    document: dict | str | None = None  # JSON dict or Markdown string
    chunks: list[ChunkOutput] = []
    stats: ProcessingStats | None = None
    output_format: OutputFormat = OutputFormat.JSON


class UrlRequest(BaseModel):
    """Request model for URL processing."""
    url: str
    output_format: OutputFormat = OutputFormat.JSON
```

---

### Step 5: Create `src/chunker.py`

```python
"""Document chunking using Docling's HybridChunker."""
from docling_core.types import DoclingDocument
from docling_core.transforms.chunker import HybridChunker
from docling_core.transforms.chunker.tokenizer import HuggingFaceTokenizer
from transformers import AutoTokenizer

from .config import MAX_TOKENS, TOKENIZER_MODEL
from .models import ChunkOutput


class DocumentChunker:
    """Wrapper for Docling's HybridChunker."""

    def __init__(self, model_name: str = TOKENIZER_MODEL, max_tokens: int = MAX_TOKENS):
        self.max_tokens = max_tokens
        self._tokenizer = None
        self._chunker = None
        self._model_name = model_name

    def _ensure_initialized(self):
        """Lazy initialization of tokenizer and chunker."""
        if self._chunker is None:
            hf_tokenizer = AutoTokenizer.from_pretrained(self._model_name)
            self._tokenizer = HuggingFaceTokenizer(
                tokenizer=hf_tokenizer,
                max_tokens=self.max_tokens
            )
            self._chunker = HybridChunker(
                tokenizer=self._tokenizer,
                max_tokens=self.max_tokens
            )

    def chunk(self, doc: DoclingDocument) -> list[ChunkOutput]:
        """Chunk a DoclingDocument into smaller pieces."""
        self._ensure_initialized()

        chunks = list(self._chunker.chunk(doc))
        result = []

        for idx, chunk in enumerate(chunks):
            # Extract page number from chunk metadata
            page_num = self._extract_page_num(chunk)

            # Count tokens
            token_count = len(self._tokenizer.tokenizer.encode(chunk.text))

            result.append(ChunkOutput(
                index=idx,
                text=chunk.text,
                page_num=page_num,
                token_count=token_count,
                preview=chunk.text[:100] + "..." if len(chunk.text) > 100 else chunk.text
            ))

        return result

    def _extract_page_num(self, chunk) -> int | None:
        """Extract page number from chunk metadata."""
        if hasattr(chunk, 'meta') and chunk.meta:
            meta = chunk.meta
            if hasattr(meta, 'doc_items') and meta.doc_items:
                for item in meta.doc_items:
                    if hasattr(item, 'prov') and item.prov:
                        for prov in item.prov:
                            if hasattr(prov, 'page_no'):
                                return prov.page_no
        return None
```

---

### Step 6: Create `src/processor.py`

```python
"""Core document processing logic using Docling."""
import tempfile
from pathlib import Path
from typing import BinaryIO

from docling.document_converter import DocumentConverter, PdfFormatOption
from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import (
    PdfPipelineOptions,
    AcceleratorOptions,
    AcceleratorDevice,
)
from docling.datamodel.pipeline_options import RapidOcrOptions
from docling_core.types import DoclingDocument
from langdetect import detect, LangDetectException

from .config import OCR_LANGUAGES, FORCE_FULL_PAGE_OCR, TEMP_DIR
from .models import (
    ProcessingResult,
    DocumentMetadata,
    ChunkOutput,
    ProcessingStats,
    OutputFormat,
)
from .chunker import DocumentChunker


class DocumentProcessor:
    """Process documents using Docling."""

    def __init__(self):
        self._converter: DocumentConverter | None = None
        self._chunker = DocumentChunker()

    def _get_converter(self) -> DocumentConverter:
        """Get or create DocumentConverter with configured options."""
        if self._converter is None:
            # Configure PDF pipeline
            accelerator = AcceleratorOptions(
                num_threads=4,
                device=AcceleratorDevice.CPU
            )
            pipeline_options = PdfPipelineOptions()
            pipeline_options.accelerator_options = accelerator
            pipeline_options.do_ocr = True
            pipeline_options.ocr_options = RapidOcrOptions(
                lang=OCR_LANGUAGES,
                force_full_page_ocr=FORCE_FULL_PAGE_OCR
            )

            self._converter = DocumentConverter(
                format_options={
                    InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)
                }
            )
        return self._converter

    async def process_file(
        self,
        file_content: bytes,
        filename: str,
        output_format: OutputFormat = OutputFormat.JSON
    ) -> ProcessingResult:
        """Process an uploaded file."""
        try:
            # Save to temp file
            suffix = Path(filename).suffix
            with tempfile.NamedTemporaryFile(
                delete=False,
                suffix=suffix,
                dir=TEMP_DIR
            ) as tmp:
                tmp.write(file_content)
                tmp_path = Path(tmp.name)

            # Process document
            result = self._process_document(tmp_path, filename, output_format)

            # Cleanup
            tmp_path.unlink(missing_ok=True)

            return result

        except Exception as e:
            return ProcessingResult(
                success=False,
                error=str(e),
                output_format=output_format
            )

    async def process_url(
        self,
        url: str,
        output_format: OutputFormat = OutputFormat.JSON
    ) -> ProcessingResult:
        """Process a document from URL."""
        try:
            # Docling can handle URLs directly
            filename = url.split("/")[-1] or "document"
            return self._process_document(url, filename, output_format)

        except Exception as e:
            return ProcessingResult(
                success=False,
                error=str(e),
                output_format=output_format
            )

    def _process_document(
        self,
        source: str | Path,
        filename: str,
        output_format: OutputFormat
    ) -> ProcessingResult:
        """Core processing logic."""
        converter = self._get_converter()

        # Convert document
        conv_result = converter.convert(source)
        doc: DoclingDocument = conv_result.document

        # Extract metadata
        metadata = self._extract_metadata(doc, filename)

        # Chunk document
        chunks = self._chunker.chunk(doc)

        # Format output based on requested format
        return self._format_output(doc, chunks, metadata, output_format)

    def _extract_metadata(
        self,
        doc: DoclingDocument,
        filename: str
    ) -> DocumentMetadata:
        """Extract metadata from DoclingDocument."""
        # Detect language from text
        text_sample = ""
        if hasattr(doc, 'texts') and doc.texts:
            text_sample = " ".join([t.text for t in doc.texts[:5] if hasattr(t, 'text')])
        elif hasattr(doc, 'export_to_markdown'):
            text_sample = doc.export_to_markdown()[:1000]

        language = "unknown"
        if text_sample:
            try:
                language = detect(text_sample)
            except LangDetectException:
                pass

        # Get page count
        page_count = None
        if hasattr(doc, 'pages'):
            page_count = len(doc.pages)

        # Determine file type
        file_type = Path(filename).suffix.lstrip('.').upper() or "UNKNOWN"

        return DocumentMetadata(
            filename=filename,
            file_type=file_type,
            page_count=page_count,
            language=language
        )

    def _format_output(
        self,
        doc: DoclingDocument,
        chunks: list[ChunkOutput],
        metadata: DocumentMetadata,
        output_format: OutputFormat
    ) -> ProcessingResult:
        """Format the processing result based on requested format."""

        if output_format == OutputFormat.JSON:
            # Full JSON output
            doc_dict = doc.export_to_dict() if hasattr(doc, 'export_to_dict') else {}
            return ProcessingResult(
                success=True,
                metadata=metadata,
                document=doc_dict,
                chunks=chunks,
                output_format=output_format
            )

        elif output_format == OutputFormat.MARKDOWN:
            # Markdown output
            markdown = doc.export_to_markdown() if hasattr(doc, 'export_to_markdown') else ""
            return ProcessingResult(
                success=True,
                metadata=metadata,
                document=markdown,
                chunks=chunks,
                output_format=output_format
            )

        else:  # SUMMARY
            # Summary with stats only
            total_tokens = sum(c.token_count for c in chunks)
            stats = ProcessingStats(
                total_chunks=len(chunks),
                total_tokens=total_tokens,
                pages_processed=metadata.page_count
            )
            # Only include preview in chunks
            summary_chunks = [
                ChunkOutput(
                    index=c.index,
                    text="",  # Don't include full text in summary
                    page_num=c.page_num,
                    token_count=c.token_count,
                    preview=c.preview
                )
                for c in chunks
            ]
            return ProcessingResult(
                success=True,
                metadata=metadata,
                document=None,
                chunks=summary_chunks,
                stats=stats,
                output_format=output_format
            )
```

---

### Step 7: Create `src/main.py`

```python
"""FastAPI application for document processing."""
import uvicorn
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from .config import HOST, PORT
from .models import ProcessingResult, OutputFormat, UrlRequest
from .processor import DocumentProcessor

app = FastAPI(
    title="Docling Document Processor",
    description="Process documents and extract structured content with chunking",
    version="0.1.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize processor
processor = DocumentProcessor()


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


@app.post("/process", response_model=ProcessingResult)
async def process_document(
    file: UploadFile | None = File(None),
    output_format: OutputFormat = Form(OutputFormat.JSON)
):
    """
    Process an uploaded document.

    - **file**: Document file (PDF, DOCX, HTML, images)
    - **output_format**: Output format (json, markdown, summary)
    """
    if not file:
        raise HTTPException(status_code=400, detail="No file provided")

    content = await file.read()
    return await processor.process_file(
        file_content=content,
        filename=file.filename or "document",
        output_format=output_format
    )


@app.post("/process/url", response_model=ProcessingResult)
async def process_url(request: UrlRequest):
    """
    Process a document from URL.

    - **url**: URL to the document
    - **output_format**: Output format (json, markdown, summary)
    """
    return await processor.process_url(
        url=request.url,
        output_format=request.output_format
    )


def run():
    """Run the server."""
    uvicorn.run(
        "src.main:app",
        host=HOST,
        port=PORT,
        reload=True
    )


if __name__ == "__main__":
    run()
```

---

### Step 8: Create `README.md`

```markdown
# Docling Document Processing Service

HTTP microservice for processing documents using Docling.

## Features

- Process PDF, DOCX, HTML, images
- Extract structured content (DoclingDocument)
- Chunk documents for RAG applications
- Multiple output formats (JSON, Markdown, Summary)

## Installation

```bash
pip install -e .
```

## Usage

### Start Server

```bash
# Using entry point
docling-service

# Or directly
uvicorn src.main:app --reload
```

### API Endpoints

#### Process File Upload

```bash
curl -X POST http://localhost:8000/process \
  -F "file=@document.pdf" \
  -F "output_format=json"
```

#### Process URL

```bash
curl -X POST http://localhost:8000/process/url \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com/doc.pdf", "output_format": "markdown"}'
```

### Output Formats

- `json` - Full DoclingDocument as JSON + chunks
- `markdown` - Document as Markdown + chunks
- `summary` - Metadata + chunk previews + stats

## Configuration

Environment variables:

- `HOST` - Server host (default: 0.0.0.0)
- `PORT` - Server port (default: 8000)
- `TEMP_DIR` - Temp directory for uploads
```

---

## Verification Commands

After creating all files, run these commands to verify:

```bash
# 1. Install the package
pip install -e .

# 2. Start the server
uvicorn src.main:app --reload --port 8000

# 3. Test health endpoint
curl http://localhost:8000/health

# 4. Test file processing (in another terminal)
curl -X POST http://localhost:8000/process \
  -F "file=@test.pdf" \
  -F "output_format=json"

# 5. Test URL processing
curl -X POST http://localhost:8000/process/url \
  -H "Content-Type: application/json" \
  -d '{"url": "https://arxiv.org/pdf/2408.09869", "output_format": "summary"}'

# 6. Test markdown output
curl -X POST http://localhost:8000/process \
  -F "file=@test.pdf" \
  -F "output_format=markdown"
```

---

## Summary

This blueprint creates a standalone document processing service with:

1. **FastAPI** HTTP server with 2 endpoints (`/process`, `/process/url`)
2. **Docling** integration for document conversion
3. **HybridChunker** for intelligent text chunking
4. **3 output formats**: JSON (full), Markdown, Summary
5. **Clean architecture**: separate modules for config, models, processing, chunking

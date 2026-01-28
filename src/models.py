"""Pydantic models for Docling Playground."""

from typing import Any

from pydantic import BaseModel, Field

from .config import (
    Accelerator,
    OCRLibrary,
    OutputFormat,
    PipelineType,
    DEFAULT_OPTIONS,
)


class ProcessingTiming(BaseModel):
    """Timing information for document processing stages."""

    total_seconds: float = Field(description="Total processing time in seconds")
    loading_seconds: float | None = Field(default=None, description="Document loading time")
    ocr_seconds: float | None = Field(default=None, description="OCR processing time")
    layout_seconds: float | None = Field(default=None, description="Layout analysis time")
    table_seconds: float | None = Field(default=None, description="Table extraction time")
    chunking_seconds: float | None = Field(default=None, description="Chunking time")

    def format_breakdown(self) -> str:
        """Format timing breakdown as a tree string."""
        lines = [f"Total Time: {self.total_seconds:.2f}s"]

        stages = [
            ("Document Loading", self.loading_seconds),
            ("OCR", self.ocr_seconds),
            ("Layout Analysis", self.layout_seconds),
            ("Table Extraction", self.table_seconds),
            ("Chunking", self.chunking_seconds),
        ]

        # Filter out None values
        active_stages = [(name, time) for name, time in stages if time is not None]

        for i, (name, time) in enumerate(active_stages):
            prefix = "└──" if i == len(active_stages) - 1 else "├──"
            lines.append(f"{prefix} {name}: {time:.2f}s")

        return "\n".join(lines)

    def format_badge(self) -> str:
        """Format timing as a badge string."""
        return f"Processed in {self.total_seconds:.2f}s"


class ProcessingOptions(BaseModel):
    """Configuration options for document processing."""

    pipeline: PipelineType = Field(default=DEFAULT_OPTIONS["pipeline"])
    accelerator: Accelerator = Field(default=DEFAULT_OPTIONS["accelerator"])

    # OCR settings
    ocr_enabled: bool = Field(default=DEFAULT_OPTIONS["ocr_enabled"])
    ocr_library: OCRLibrary = Field(default=DEFAULT_OPTIONS["ocr_library"])
    ocr_languages: list[str] = Field(default_factory=lambda: DEFAULT_OPTIONS["ocr_languages"].copy())
    force_full_page_ocr: bool = Field(default=DEFAULT_OPTIONS["force_full_page_ocr"])

    # Advanced features
    do_table_structure: bool = Field(default=DEFAULT_OPTIONS["do_table_structure"])
    do_code_enrichment: bool = Field(default=DEFAULT_OPTIONS["do_code_enrichment"])
    do_formula_enrichment: bool = Field(default=DEFAULT_OPTIONS["do_formula_enrichment"])
    do_picture_description: bool = Field(default=DEFAULT_OPTIONS["do_picture_description"])

    # Output settings
    output_format: OutputFormat = Field(default=DEFAULT_OPTIONS["output_format"])
    chunk_max_tokens: int = Field(default=DEFAULT_OPTIONS["chunk_max_tokens"])


class ChunkInfo(BaseModel):
    """Information about a document chunk."""

    index: int = Field(description="Chunk index")
    text: str = Field(description="Full chunk text")
    preview: str = Field(description="Truncated preview of chunk text")
    page_num: int | None = Field(default=None, description="Page number if available")
    token_count: int = Field(description="Approximate token count")


class ProcessingStats(BaseModel):
    """Statistics about document processing."""

    num_pages: int = Field(default=0, description="Number of pages processed")
    num_tables: int = Field(default=0, description="Number of tables extracted")
    num_figures: int = Field(default=0, description="Number of figures found")
    num_chunks: int = Field(default=0, description="Number of chunks created")
    total_tokens: int = Field(default=0, description="Total tokens across all chunks")
    ocr_library_used: str | None = Field(default=None, description="OCR library used")
    pipeline_used: str = Field(default="standard", description="Pipeline type used")


class ProcessingResult(BaseModel):
    """Result of document processing."""

    success: bool = Field(description="Whether processing succeeded")
    error: str | None = Field(default=None, description="Error message if failed")

    # Document output
    markdown: str = Field(default="", description="Markdown representation")
    json_data: dict[str, Any] = Field(default_factory=dict, description="Full DoclingDocument as dict")

    # Chunks
    chunks: list[ChunkInfo] = Field(default_factory=list, description="Document chunks")

    # Metadata
    stats: ProcessingStats = Field(default_factory=ProcessingStats)
    timing: ProcessingTiming | None = Field(default=None, description="Processing timing breakdown")

    def get_timing_badge(self) -> str:
        """Get formatted timing badge."""
        if self.timing:
            return self.timing.format_badge()
        return ""

    def get_timing_breakdown(self) -> str:
        """Get formatted timing breakdown."""
        if self.timing:
            return self.timing.format_breakdown()
        return "No timing information available"


class ModelStatus(BaseModel):
    """Status of a downloadable model."""

    id: str = Field(description="Model identifier")
    name: str = Field(description="Display name")
    description: str = Field(description="Model description")
    size_mb: int = Field(description="Approximate size in MB")
    required: bool = Field(description="Whether model is required for basic operation")
    downloaded: bool = Field(description="Whether model is downloaded")
    path: str | None = Field(default=None, description="Path to downloaded model")

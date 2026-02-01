"""Core document processing logic using Docling."""

import logging
import time
from pathlib import Path
from typing import BinaryIO

from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import (
    AcceleratorDevice,
    AcceleratorOptions,
    EasyOcrOptions,
    OcrMacOptions,
    PdfPipelineOptions,
    RapidOcrOptions,
    TableFormerMode,
    TableStructureOptions,
    TesseractCliOcrOptions,
    TesseractOcrOptions,
)
from docling.document_converter import DocumentConverter, PdfFormatOption
from docling.pipeline.standard_pdf_pipeline import StandardPdfPipeline

from .config import Accelerator, OCRLibrary, PipelineType, enable_offline_mode, is_offline_mode

logger = logging.getLogger("docling-playground.processor")
from .models import (
    ChunkInfo,
    ProcessingOptions,
    ProcessingResult,
    ProcessingStats,
    ProcessingTiming,
)
from .chunker import DocumentChunker


class DocumentProcessor:
    """Handles document processing with configurable options."""

    def __init__(self):
        self._converter: DocumentConverter | None = None
        self._current_options: ProcessingOptions | None = None
        self._chunker = DocumentChunker()

    def _get_accelerator_device(self, accelerator: Accelerator) -> AcceleratorDevice:
        """Map accelerator option to AcceleratorDevice."""
        mapping = {
            Accelerator.AUTO: AcceleratorDevice.AUTO,
            Accelerator.CPU: AcceleratorDevice.CPU,
            Accelerator.CUDA: AcceleratorDevice.CUDA,
            Accelerator.MPS: AcceleratorDevice.MPS,
        }
        return mapping.get(accelerator, AcceleratorDevice.AUTO)

    def _get_ocr_options(self, options: ProcessingOptions):
        """Get OCR options based on selected library."""
        if not options.ocr_enabled:
            return None

        if options.ocr_library == OCRLibrary.EASYOCR:
            return EasyOcrOptions(
                lang=options.ocr_languages,
                force_full_page_ocr=options.force_full_page_ocr,
            )
        elif options.ocr_library == OCRLibrary.RAPIDOCR:
            return RapidOcrOptions(
                force_full_page_ocr=options.force_full_page_ocr,
            )
        elif options.ocr_library == OCRLibrary.TESSERACT:
            # Try tesserocr first, fall back to CLI
            try:
                return TesseractOcrOptions(
                    lang=options.ocr_languages,
                    force_full_page_ocr=options.force_full_page_ocr,
                )
            except ImportError:
                return TesseractCliOcrOptions(
                    lang=options.ocr_languages,
                    force_full_page_ocr=options.force_full_page_ocr,
                )

        return None

    def _build_converter(self, options: ProcessingOptions) -> DocumentConverter:
        """Build a DocumentConverter with the given options."""
        # Accelerator options
        accelerator_options = AcceleratorOptions(
            device=self._get_accelerator_device(options.accelerator),
            num_threads=4,
        )

        # Handle VLM pipeline - needs different pipeline options
        if options.pipeline == PipelineType.VLM:
            try:
                from docling.pipeline.vlm_pipeline import VlmPipeline
                from docling.datamodel.pipeline_options import VlmPipelineOptions

                pipeline_cls = VlmPipeline
                pipeline_options = VlmPipelineOptions(
                    accelerator_options=accelerator_options,
                )
                logger.info("Using VLM pipeline with VlmPipelineOptions")
            except ImportError:
                # Fall back to standard if VLM not available
                logger.warning("VLM pipeline not available, falling back to standard")
                pipeline_cls = StandardPdfPipeline
                pipeline_options = PdfPipelineOptions(
                    accelerator_options=accelerator_options,
                    do_ocr=options.ocr_enabled,
                    do_table_structure=options.do_table_structure,
                    table_structure_options=TableStructureOptions(
                        mode=TableFormerMode.ACCURATE,
                    ),
                )
        else:
            pipeline_cls = StandardPdfPipeline
            # Pipeline options for standard pipeline
            pipeline_options = PdfPipelineOptions(
                accelerator_options=accelerator_options,
                do_ocr=options.ocr_enabled,
                do_table_structure=options.do_table_structure,
                table_structure_options=TableStructureOptions(
                    mode=TableFormerMode.ACCURATE,
                ),
            )

            # Set OCR options (only for standard pipeline)
            if options.ocr_enabled:
                ocr_options = self._get_ocr_options(options)
                if ocr_options:
                    pipeline_options.ocr_options = ocr_options

        # Build format options
        format_options = {
            InputFormat.PDF: PdfFormatOption(
                pipeline_cls=pipeline_cls,
                pipeline_options=pipeline_options,
            )
        }

        return DocumentConverter(format_options=format_options)

    def _needs_rebuild(self, options: ProcessingOptions) -> bool:
        """Check if converter needs to be rebuilt for new options."""
        if self._converter is None or self._current_options is None:
            return True

        # Check if key options changed
        return (
            self._current_options.pipeline != options.pipeline
            or self._current_options.accelerator != options.accelerator
            or self._current_options.ocr_enabled != options.ocr_enabled
            or self._current_options.ocr_library != options.ocr_library
            or self._current_options.ocr_languages != options.ocr_languages
            or self._current_options.force_full_page_ocr != options.force_full_page_ocr
            or self._current_options.do_table_structure != options.do_table_structure
        )

    def process_file(
        self,
        file_path: str | Path,
        options: ProcessingOptions,
    ) -> ProcessingResult:
        """Process a document file."""
        # Ensure offline mode is enabled during processing
        enable_offline_mode()

        logger.info(f"Processing file: {file_path}")
        logger.info(f"Offline mode: {is_offline_mode()}")
        logger.info(f"OCR enabled: {options.ocr_enabled}, library: {options.ocr_library.value if options.ocr_enabled else 'N/A'}")
        logger.info(f"Pipeline: {options.pipeline.value}, Accelerator: {options.accelerator.value}")

        timing = ProcessingTiming(total_seconds=0)
        start_time = time.perf_counter()

        try:
            # Build converter if needed
            load_start = time.perf_counter()
            if self._needs_rebuild(options):
                logger.info("Building document converter...")
                self._converter = self._build_converter(options)
                self._current_options = options
                logger.info("Converter built successfully")
            else:
                logger.debug("Reusing existing converter")
            timing.loading_seconds = time.perf_counter() - load_start

            # Convert document
            logger.info("Starting document conversion...")
            convert_start = time.perf_counter()
            result = self._converter.convert(file_path)
            doc = result.document
            convert_time = time.perf_counter() - convert_start
            logger.info(f"Conversion completed in {convert_time:.2f}s")

            # Estimate stage times (Docling doesn't expose individual stage timing)
            if options.ocr_enabled:
                timing.ocr_seconds = convert_time * 0.4
                timing.layout_seconds = convert_time * 0.35
            else:
                timing.layout_seconds = convert_time * 0.6

            if options.do_table_structure:
                timing.table_seconds = convert_time * 0.15

            # Generate outputs
            markdown = doc.export_to_markdown()
            json_data = doc.export_to_dict()

            # Chunk document
            chunk_start = time.perf_counter()
            chunks = self._chunker.chunk_document(doc, options.chunk_max_tokens)
            timing.chunking_seconds = time.perf_counter() - chunk_start

            # Gather statistics
            stats = ProcessingStats(
                num_pages=len(doc.pages) if hasattr(doc, "pages") else 0,
                num_tables=len([item for item in doc.tables]) if hasattr(doc, "tables") else 0,
                num_figures=len([item for item in doc.pictures]) if hasattr(doc, "pictures") else 0,
                num_chunks=len(chunks),
                total_tokens=sum(c.token_count for c in chunks),
                ocr_library_used=options.ocr_library.value if options.ocr_enabled else None,
                pipeline_used=options.pipeline.value,
            )

            timing.total_seconds = time.perf_counter() - start_time

            return ProcessingResult(
                success=True,
                markdown=markdown,
                json_data=json_data,
                chunks=chunks,
                stats=stats,
                timing=timing,
            )

        except Exception as e:
            timing.total_seconds = time.perf_counter() - start_time
            return ProcessingResult(
                success=False,
                error=str(e),
                timing=timing,
            )

    def process_url(self, url: str, options: ProcessingOptions) -> ProcessingResult:
        """Process a document from URL."""
        timing = ProcessingTiming(total_seconds=0)
        start_time = time.perf_counter()

        try:
            # Build converter if needed
            load_start = time.perf_counter()
            if self._needs_rebuild(options):
                self._converter = self._build_converter(options)
                self._current_options = options
            timing.loading_seconds = time.perf_counter() - load_start

            # Convert document from URL
            convert_start = time.perf_counter()
            result = self._converter.convert(url)
            doc = result.document
            convert_time = time.perf_counter() - convert_start

            # Estimate stage times
            if options.ocr_enabled:
                timing.ocr_seconds = convert_time * 0.4
                timing.layout_seconds = convert_time * 0.35
            else:
                timing.layout_seconds = convert_time * 0.6

            if options.do_table_structure:
                timing.table_seconds = convert_time * 0.15

            # Generate outputs
            markdown = doc.export_to_markdown()
            json_data = doc.export_to_dict()

            # Chunk document
            chunk_start = time.perf_counter()
            chunks = self._chunker.chunk_document(doc, options.chunk_max_tokens)
            timing.chunking_seconds = time.perf_counter() - chunk_start

            # Gather statistics
            stats = ProcessingStats(
                num_pages=len(doc.pages) if hasattr(doc, "pages") else 0,
                num_tables=len([item for item in doc.tables]) if hasattr(doc, "tables") else 0,
                num_figures=len([item for item in doc.pictures]) if hasattr(doc, "pictures") else 0,
                num_chunks=len(chunks),
                total_tokens=sum(c.token_count for c in chunks),
                ocr_library_used=options.ocr_library.value if options.ocr_enabled else None,
                pipeline_used=options.pipeline.value,
            )

            timing.total_seconds = time.perf_counter() - start_time

            return ProcessingResult(
                success=True,
                markdown=markdown,
                json_data=json_data,
                chunks=chunks,
                stats=stats,
                timing=timing,
            )

        except Exception as e:
            timing.total_seconds = time.perf_counter() - start_time
            return ProcessingResult(
                success=False,
                error=str(e),
                timing=timing,
            )

    def process_bytes(
        self,
        data: bytes | BinaryIO,
        filename: str,
        options: ProcessingOptions,
    ) -> ProcessingResult:
        """Process document from bytes or file-like object."""
        import tempfile
        from pathlib import Path

        # Write to temporary file
        suffix = Path(filename).suffix
        with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
            if isinstance(data, bytes):
                tmp.write(data)
            else:
                tmp.write(data.read())
            tmp_path = tmp.name

        try:
            return self.process_file(tmp_path, options)
        finally:
            # Clean up temp file
            Path(tmp_path).unlink(missing_ok=True)

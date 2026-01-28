"""Main Gradio application for Docling Playground."""

import gradio as gr

from .config import (
    Accelerator,
    OCRLibrary,
    OutputFormat,
    PipelineType,
    DEFAULT_SERVER_HOST,
    DEFAULT_SERVER_PORT,
    MODELS_DIR,
    setup_offline_environment,
)
from .models import ProcessingOptions
from .processor import DocumentProcessor
from .components.parameter_panel import create_parameter_panel
from .components.input_panel import create_input_panel
from .components.result_display import (
    create_result_display,
    format_timing_badge,
    format_timing_breakdown,
    format_chunks_info,
    format_chunks_table,
    format_stats,
)
from .components.model_panel import create_model_panel


# Global processor instance (reused across requests)
_processor = DocumentProcessor()


def process_document(
    file,
    pipeline,
    accelerator,
    ocr_enabled,
    ocr_library,
    ocr_languages,
    force_full_page_ocr,
    do_table_structure,
    do_code_enrichment,
    do_formula_enrichment,
    do_picture_description,
    output_format,
    chunk_max_tokens,
):
    """Process a document with the given parameters.

    Returns tuple of outputs for all result display components.
    """
    # Validate input
    if file is None:
        return (
            "Please upload a file",  # timing_display
            None,  # original_view
            "No file uploaded",  # processed_view
            "No file uploaded",  # markdown_output
            "",  # markdown_raw
            None,  # json_output
            "",  # chunks_info
            [],  # chunks_table
            "",  # timing_breakdown
            None,  # stats_output
        )

    # Build processing options
    options = ProcessingOptions(
        pipeline=PipelineType(pipeline),
        accelerator=Accelerator(accelerator),
        ocr_enabled=ocr_enabled,
        ocr_library=OCRLibrary(ocr_library),
        ocr_languages=ocr_languages if ocr_languages else ["en"],
        force_full_page_ocr=force_full_page_ocr,
        do_table_structure=do_table_structure,
        do_code_enrichment=do_code_enrichment,
        do_formula_enrichment=do_formula_enrichment,
        do_picture_description=do_picture_description,
        output_format=OutputFormat(output_format),
        chunk_max_tokens=int(chunk_max_tokens),
    )

    # Process document - file is a Gradio file object with .name attribute
    file_path = file.name if hasattr(file, "name") else file
    result = _processor.process_file(file_path, options)
    original_file = file

    # Handle errors
    if not result.success:
        error_msg = f"**Error:** {result.error}"
        return (
            format_timing_badge(result.timing),  # timing_display
            original_file,  # original_view
            error_msg,  # processed_view
            error_msg,  # markdown_output
            "",  # markdown_raw
            None,  # json_output
            "",  # chunks_info
            [],  # chunks_table
            format_timing_breakdown(result.timing),  # timing_breakdown
            None,  # stats_output
        )

    # Format successful results
    timing_badge = format_timing_badge(result.timing)
    timing_breakdown = format_timing_breakdown(result.timing)
    chunks_info = format_chunks_info(result.chunks)
    chunks_table = format_chunks_table(result.chunks)
    stats = format_stats(result.stats)

    # Truncate markdown for preview if too long
    markdown_preview = result.markdown
    if len(markdown_preview) > 50000:
        markdown_preview = markdown_preview[:50000] + "\n\n... (truncated)"

    return (
        timing_badge,  # timing_display
        original_file,  # original_view
        markdown_preview,  # processed_view
        markdown_preview,  # markdown_output
        result.markdown,  # markdown_raw
        result.json_data,  # json_output
        chunks_info,  # chunks_info
        chunks_table,  # chunks_table
        timing_breakdown,  # timing_breakdown
        stats,  # stats_output
    )


def create_app(theme=None, css=None) -> gr.Blocks:
    """Create the Gradio application."""

    # Custom CSS for styling
    custom_css = css or """
    .timing-badge {
        background-color: #e8f5e9;
        padding: 10px 15px;
        border-radius: 8px;
        border-left: 4px solid #4caf50;
        margin-bottom: 15px;
    }
    .timing-badge h3 {
        margin: 0;
        color: #2e7d32;
    }
    .error-display {
        background-color: #ffebee;
        padding: 15px;
        border-radius: 8px;
        border-left: 4px solid #f44336;
    }
    .chunks-info {
        background-color: #e3f2fd;
        padding: 10px 15px;
        border-radius: 8px;
        margin-bottom: 10px;
    }
    .input-hint {
        font-size: 0.85em;
        color: #666;
    }
    .download-progress {
        padding: 10px;
        background-color: #fff3e0;
        border-radius: 4px;
        margin-top: 10px;
    }
    """

    with gr.Blocks(
        title="Docling Playground",
    ) as app:
        # Header
        gr.Markdown("# Docling Playground")
        gr.Markdown(
            "Experiment with document processing parameters and visualize results in real-time."
        )

        with gr.Tabs():
            # Main processing tab
            with gr.Tab("Process Documents"):
                with gr.Row():
                    # Left column: Parameters and Input
                    with gr.Column(scale=1):
                        params = create_parameter_panel()
                        inputs = create_input_panel()

                    # Right column: Results
                    with gr.Column(scale=2):
                        outputs = create_result_display()

                # Wire up the process button
                inputs["process_btn"].click(
                    fn=process_document,
                    inputs=[
                        inputs["file_input"],
                        params["pipeline"],
                        params["accelerator"],
                        params["ocr_enabled"],
                        params["ocr_library"],
                        params["ocr_languages"],
                        params["force_full_page_ocr"],
                        params["do_table_structure"],
                        params["do_code_enrichment"],
                        params["do_formula_enrichment"],
                        params["do_picture_description"],
                        params["output_format"],
                        params["chunk_max_tokens"],
                    ],
                    outputs=[
                        outputs["timing_display"],
                        outputs["original_view"],
                        outputs["processed_view"],
                        outputs["markdown_output"],
                        outputs["markdown_raw"],
                        outputs["json_output"],
                        outputs["chunks_info"],
                        outputs["chunks_table"],
                        outputs["timing_breakdown"],
                        outputs["stats_output"],
                    ],
                )

            # Model management tab
            with gr.Tab("Model Management"):
                model_components = create_model_panel()

        # Footer
        gr.Markdown("---")
        gr.Markdown(
            "Powered by [Docling](https://github.com/docling-project/docling) | "
            "[Documentation](https://docling-project.github.io/docling/)"
        )

    return app


def main(
    host: str = DEFAULT_SERVER_HOST,
    port: int = DEFAULT_SERVER_PORT,
    share: bool = False,
):
    """Launch the Gradio application.

    Args:
        host: Server host address
        port: Server port number
        share: Whether to create a public Gradio link
    """
    # Custom CSS for styling
    custom_css = """
    .timing-badge {
        background-color: #e8f5e9;
        padding: 10px 15px;
        border-radius: 8px;
        border-left: 4px solid #4caf50;
        margin-bottom: 15px;
    }
    .timing-badge h3 {
        margin: 0;
        color: #2e7d32;
    }
    .error-display {
        background-color: #ffebee;
        padding: 15px;
        border-radius: 8px;
        border-left: 4px solid #f44336;
    }
    .chunks-info {
        background-color: #e3f2fd;
        padding: 10px 15px;
        border-radius: 8px;
        margin-bottom: 10px;
    }
    .input-hint {
        font-size: 0.85em;
        color: #666;
    }
    .download-progress {
        padding: 10px;
        background-color: #fff3e0;
        border-radius: 4px;
        margin-top: 10px;
    }
    """

    app = create_app()
    app.launch(
        server_name=host,
        server_port=port,
        share=share,
        theme=gr.themes.Soft(),
        css=custom_css,
    )


if __name__ == "__main__":
    main()

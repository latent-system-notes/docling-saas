"""Result display panel for Docling Playground."""

import gradio as gr


def create_result_display() -> dict:
    """Create the result display panel with tabs.

    Returns:
        Dictionary of Gradio components for displaying results
    """
    # Prominent timing display at top
    timing_display = gr.Markdown(
        value="",
        elem_classes=["timing-badge"],
    )

    with gr.Tabs():
        # Side-by-side view
        with gr.Tab("Side-by-Side"):
            with gr.Row():
                with gr.Column(scale=1):
                    original_view = gr.File(
                        label="Original Document",
                        interactive=False,
                    )
                with gr.Column(scale=1):
                    processed_view = gr.Markdown(
                        label="Processed Output",
                        value="",
                    )

        # Markdown preview
        with gr.Tab("Markdown"):
            markdown_output = gr.Markdown(
                value="",
                label="Markdown Output",
            )
            markdown_raw = gr.Code(
                value="",
                language="markdown",
                label="Raw Markdown",
                lines=20,
            )

        # JSON viewer
        with gr.Tab("JSON"):
            json_output = gr.JSON(
                value=None,
                label="DoclingDocument",
            )

        # Chunks table
        with gr.Tab("Chunks"):
            chunks_info = gr.Markdown(
                value="",
                elem_classes=["chunks-info"],
            )
            chunks_table = gr.Dataframe(
                headers=["#", "Preview", "Page", "Tokens"],
                datatype=["number", "str", "number", "number"],
                label="Document Chunks",
                wrap=True,
                row_count=10,
            )

        # Stats tab with timing breakdown
        with gr.Tab("Stats"):
            gr.Markdown("### Processing Statistics")

            # Timing breakdown
            timing_breakdown = gr.Markdown(
                value="",
                label="Timing Breakdown",
            )

            # Other stats
            stats_output = gr.JSON(
                value=None,
                label="Processing Statistics",
            )

        # Errors tab (hidden by default)
        with gr.Tab("Errors", visible=False) as errors_tab:
            error_output = gr.Markdown(
                value="",
                elem_classes=["error-display"],
            )

    return {
        "timing_display": timing_display,
        "original_view": original_view,
        "processed_view": processed_view,
        "markdown_output": markdown_output,
        "markdown_raw": markdown_raw,
        "json_output": json_output,
        "chunks_info": chunks_info,
        "chunks_table": chunks_table,
        "timing_breakdown": timing_breakdown,
        "stats_output": stats_output,
        "errors_tab": errors_tab,
        "error_output": error_output,
    }


def format_timing_badge(timing) -> str:
    """Format timing as a badge for display."""
    if timing is None:
        return ""
    return f"### Processed in {timing.total_seconds:.2f}s"


def format_timing_breakdown(timing) -> str:
    """Format timing breakdown for display."""
    if timing is None:
        return "No timing information available"

    lines = [
        "```",
        f"Total Time: {timing.total_seconds:.2f}s",
    ]

    stages = [
        ("Document Loading", timing.loading_seconds),
        ("OCR", timing.ocr_seconds),
        ("Layout Analysis", timing.layout_seconds),
        ("Table Extraction", timing.table_seconds),
        ("Chunking", timing.chunking_seconds),
    ]

    # Filter out None values
    active_stages = [(name, t) for name, t in stages if t is not None]

    for i, (name, t) in enumerate(active_stages):
        prefix = "" if i == len(active_stages) - 1 else ""
        lines.append(f"{prefix} {name}: {t:.2f}s")

    lines.append("```")
    return "\n".join(lines)


def format_chunks_info(chunks: list) -> str:
    """Format chunks summary info."""
    if not chunks:
        return "No chunks generated"

    total_tokens = sum(c.token_count for c in chunks)
    return f"**{len(chunks)} chunks** | **{total_tokens:,} total tokens**"


def format_chunks_table(chunks: list) -> list[list]:
    """Format chunks as table data."""
    if not chunks:
        return []

    return [
        [c.index, c.preview, c.page_num or "-", c.token_count]
        for c in chunks
    ]


def format_stats(stats) -> dict:
    """Format stats for JSON display."""
    if stats is None:
        return {}

    return {
        "Pages": stats.num_pages,
        "Tables": stats.num_tables,
        "Figures": stats.num_figures,
        "Chunks": stats.num_chunks,
        "Total Tokens": stats.total_tokens,
        "OCR Library": stats.ocr_library_used or "None",
        "Pipeline": stats.pipeline_used,
    }

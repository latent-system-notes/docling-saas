"""File upload input panel for Docling Playground."""

import gradio as gr

from ..config import SUPPORTED_FILE_EXTENSIONS


def create_input_panel() -> dict:
    """Create the input panel for file upload.

    Returns:
        Dictionary of Gradio components for inputs
    """
    with gr.Group():
        gr.Markdown("### Document Input")

        file_input = gr.File(
            label="Upload Document",
            file_types=SUPPORTED_FILE_EXTENSIONS,
            file_count="single",
        )
        gr.Markdown(
            f"**Supported formats:** {', '.join(SUPPORTED_FILE_EXTENSIONS)}",
            elem_classes=["input-hint"],
        )

        # Process button
        process_btn = gr.Button(
            "Process Document",
            variant="primary",
            size="lg",
        )

        # Clear button
        clear_btn = gr.Button(
            "Clear",
            variant="secondary",
            size="sm",
        )

    # Clear functionality
    def clear_inputs():
        return None

    clear_btn.click(
        fn=clear_inputs,
        inputs=[],
        outputs=[file_input],
    )

    return {
        "file_input": file_input,
        "process_btn": process_btn,
        "clear_btn": clear_btn,
    }

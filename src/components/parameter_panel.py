"""Parameter configuration panel for Docling Playground."""

import gradio as gr

from ..config import (
    Accelerator,
    OCRLibrary,
    OCR_LANGUAGES,
    OutputFormat,
    PipelineType,
    DEFAULT_OPTIONS,
)


def create_parameter_panel() -> dict:
    """Create the parameter configuration panel.

    Returns:
        Dictionary of Gradio components for parameters
    """
    with gr.Accordion("Processing Options", open=True):
        # Pipeline selection
        pipeline = gr.Dropdown(
            choices=[p.value for p in PipelineType],
            value=DEFAULT_OPTIONS["pipeline"].value,
            label="Pipeline",
            info="Standard: Fast and reliable. VLM: Vision-Language Model for complex documents.",
        )

        # Accelerator selection
        accelerator = gr.Dropdown(
            choices=[a.value for a in Accelerator],
            value=DEFAULT_OPTIONS["accelerator"].value,
            label="Accelerator",
            info="AUTO detects available hardware automatically.",
        )

        # OCR Settings Group
        with gr.Group():
            gr.Markdown("### OCR Settings")

            ocr_enabled = gr.Checkbox(
                value=DEFAULT_OPTIONS["ocr_enabled"],
                label="Enable OCR",
                info="Extract text from images and scanned documents",
            )

            # OCR Library Selection
            ocr_library = gr.Dropdown(
                choices=[lib.value for lib in OCRLibrary],
                value=DEFAULT_OPTIONS["ocr_library"].value,
                label="OCR Library",
                info="Choose OCR engine (disabled when OCR is off)",
                interactive=True,
            )

            # Language selection - use union of all languages so API validation
            # accepts any valid language code regardless of selected OCR library
            all_languages = sorted(set(
                lang for langs in OCR_LANGUAGES.values() for lang in langs
            ))
            ocr_languages = gr.Dropdown(
                choices=all_languages,
                value=DEFAULT_OPTIONS["ocr_languages"],
                multiselect=True,
                label="Languages",
                info="Available languages vary by OCR library",
            )

            force_full_page_ocr = gr.Checkbox(
                value=DEFAULT_OPTIONS["force_full_page_ocr"],
                label="Force Full Page OCR",
                info="Process entire page with OCR instead of detected text regions",
            )

        # Advanced Features Group
        with gr.Group():
            gr.Markdown("### Advanced Features")

            do_table_structure = gr.Checkbox(
                value=DEFAULT_OPTIONS["do_table_structure"],
                label="Table Structure Extraction",
                info="Extract table structure and cell contents",
            )

            do_code_enrichment = gr.Checkbox(
                value=DEFAULT_OPTIONS["do_code_enrichment"],
                label="Code Enrichment",
                info="Detect and format code blocks",
            )

            do_formula_enrichment = gr.Checkbox(
                value=DEFAULT_OPTIONS["do_formula_enrichment"],
                label="Formula Enrichment",
                info="Detect and extract mathematical formulas",
            )

            do_picture_description = gr.Checkbox(
                value=DEFAULT_OPTIONS["do_picture_description"],
                label="Picture Description (VLM)",
                info="Generate descriptions for images using Vision-Language Model",
            )

        # Output Settings Group
        with gr.Group():
            gr.Markdown("### Output Settings")

            output_format = gr.Dropdown(
                choices=[f.value for f in OutputFormat],
                value=DEFAULT_OPTIONS["output_format"].value,
                label="Output Format",
            )

            chunk_max_tokens = gr.Slider(
                minimum=128,
                maximum=2048,
                value=DEFAULT_OPTIONS["chunk_max_tokens"],
                step=64,
                label="Chunk Max Tokens",
                info="Maximum tokens per chunk",
            )

    # Event handlers for dynamic updates

    # Disable OCR library dropdown when OCR is disabled
    def update_ocr_library_interactive(ocr_on):
        return gr.update(interactive=ocr_on)

    ocr_enabled.change(
        fn=update_ocr_library_interactive,
        inputs=[ocr_enabled],
        outputs=[ocr_library],
    )

    # Disable language selection when OCR is disabled
    def update_languages_interactive(ocr_on):
        return gr.update(interactive=ocr_on)

    ocr_enabled.change(
        fn=update_languages_interactive,
        inputs=[ocr_enabled],
        outputs=[ocr_languages],
    )

    # Update language choices when OCR library changes
    def update_language_choices(library):
        lib_enum = OCRLibrary(library)
        choices = OCR_LANGUAGES.get(lib_enum, ["en"])
        return gr.update(choices=choices, value=[choices[0]] if choices else [])

    ocr_library.change(
        fn=update_language_choices,
        inputs=[ocr_library],
        outputs=[ocr_languages],
    )

    # Enable picture description automatically when VLM pipeline is selected
    def update_vlm_features(pipe):
        if pipe == PipelineType.VLM.value:
            return gr.update(value=True)
        return gr.update()

    pipeline.change(
        fn=update_vlm_features,
        inputs=[pipeline],
        outputs=[do_picture_description],
    )

    return {
        "pipeline": pipeline,
        "accelerator": accelerator,
        "ocr_enabled": ocr_enabled,
        "ocr_library": ocr_library,
        "ocr_languages": ocr_languages,
        "force_full_page_ocr": force_full_page_ocr,
        "do_table_structure": do_table_structure,
        "do_code_enrichment": do_code_enrichment,
        "do_formula_enrichment": do_formula_enrichment,
        "do_picture_description": do_picture_description,
        "output_format": output_format,
        "chunk_max_tokens": chunk_max_tokens,
    }

"""Model management panel for Docling Playground."""

import gradio as gr

from ..model_manager import ModelManager


def create_model_panel() -> dict:
    """Create the model management panel.

    Returns:
        Dictionary of Gradio components for model management
    """
    manager = ModelManager()

    gr.Markdown("### Offline Model Management")
    gr.Markdown(
        "Download models for offline use. Required models are needed for basic operation."
    )

    # Models directory path
    models_path = gr.Textbox(
        value=manager.artifacts_path,
        label="Models Directory",
        info="Path where models are stored",
        interactive=False,
    )

    # Model status table
    model_table = gr.Dataframe(
        headers=["Model", "Status", "Size", "Action"],
        datatype=["str", "str", "str", "str"],
        value=manager.get_model_table_data(),
        label="Available Models",
        interactive=False,
    )

    # Download progress
    download_progress = gr.Markdown(
        value="",
        elem_classes=["download-progress"],
    )

    # Action buttons
    with gr.Row():
        download_required_btn = gr.Button(
            "Download Required",
            variant="primary",
        )
        download_all_btn = gr.Button(
            "Download All",
            variant="secondary",
        )
        refresh_btn = gr.Button(
            "Refresh",
            variant="secondary",
        )

    # Offline mode indicator (always on)
    gr.Markdown("**Offline Mode: Always Enabled** (using local models from ./models)")

    # Clear cache button (with confirmation)
    with gr.Row():
        clear_cache_btn = gr.Button(
            "Clear Cache",
            variant="stop",
            size="sm",
        )

    # Event handlers

    def refresh_table():
        """Refresh the model status table."""
        mgr = ModelManager()
        return mgr.get_model_table_data()

    refresh_btn.click(
        fn=refresh_table,
        inputs=[],
        outputs=[model_table],
    )

    def download_required_models():
        """Download all required models."""
        mgr = ModelManager()
        messages = []

        def progress_callback(msg):
            messages.append(msg)

        results = mgr.download_required(progress_callback=progress_callback)

        success_count = sum(1 for v in results.values() if v)
        total_count = len(results)

        status_msg = f"Downloaded {success_count}/{total_count} required models"
        return mgr.get_model_table_data(), status_msg

    download_required_btn.click(
        fn=download_required_models,
        inputs=[],
        outputs=[model_table, download_progress],
    )

    def download_all_models():
        """Download all models including optional."""
        mgr = ModelManager()
        messages = []

        def progress_callback(msg):
            messages.append(msg)

        results = mgr.download_all(include_optional=True, progress_callback=progress_callback)

        success_count = sum(1 for v in results.values() if v)
        total_count = len(results)

        status_msg = f"Downloaded {success_count}/{total_count} models"
        return mgr.get_model_table_data(), status_msg

    download_all_btn.click(
        fn=download_all_models,
        inputs=[],
        outputs=[model_table, download_progress],
    )

    def clear_cache():
        """Clear the model cache."""
        mgr = ModelManager()
        if mgr.clear_cache():
            return mgr.get_model_table_data(), "Cache cleared successfully"
        return mgr.get_model_table_data(), "Failed to clear cache"

    clear_cache_btn.click(
        fn=clear_cache,
        inputs=[],
        outputs=[model_table, download_progress],
    )

    return {
        "models_path": models_path,
        "model_table": model_table,
        "download_progress": download_progress,
        "download_required_btn": download_required_btn,
        "download_all_btn": download_all_btn,
        "refresh_btn": refresh_btn,
        "clear_cache_btn": clear_cache_btn,
    }

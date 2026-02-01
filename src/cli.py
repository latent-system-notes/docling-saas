"""CLI entry point for Docling Playground."""

import os

import click
from rich.console import Console
from rich.table import Table

console = Console()


@click.group()
@click.version_option(version="0.1.0", prog_name="docling-playground")
def cli():
    """Docling Playground - Interactive document processing."""
    pass


@cli.group()
def models():
    """Model management commands."""
    pass


@models.command("download")
@click.option(
    "-o", "--output",
    default=None,
    type=click.Path(),
    help="Output directory for models (default: ./models)",
)
@click.option(
    "--all",
    "download_all",
    is_flag=True,
    help="Download all models including optional",
)
@click.option(
    "--docling",
    is_flag=True,
    help="Download Docling core models (layout + docling-models)",
)
@click.option(
    "--vlm",
    is_flag=True,
    help="Download VLM model (large, ~5GB)",
)
@click.option(
    "--easyocr",
    is_flag=True,
    help="Download EasyOCR models (English + Arabic)",
)
@click.option(
    "--easyocr-lang",
    multiple=True,
    default=None,
    help="Specific EasyOCR languages to download (e.g., --easyocr-lang en --easyocr-lang ar)",
)
def download(output, download_all, docling, vlm, easyocr, easyocr_lang):
    """Download models to ./models directory for offline use."""
    from .config import disable_offline_mode
    from .model_manager import ModelManager

    # Disable offline mode for downloads
    disable_offline_mode()

    manager = ModelManager(models_dir=output)

    def progress_callback(msg):
        console.print(f"  {msg}")

    console.print(f"[bold]Models directory: {manager.models_dir}[/bold]")
    console.print()

    if download_all:
        console.print("[bold]Downloading all models...[/bold]")

        # Download HuggingFace models
        results = manager.download_all(include_optional=True, progress_callback=progress_callback)

        # Download EasyOCR with default languages
        console.print("  Downloading EasyOCR (en, ar)...")
        manager.download_easyocr_model(["en", "ar"], progress_callback=progress_callback)

        success_count = sum(1 for v in results.values() if v)
        console.print(f"[green]Downloaded {success_count}/{len(results)} models[/green]")
        return

    downloaded = False

    if docling:
        console.print("[bold]Downloading Docling core models...[/bold]")
        manager.download_hf_model("docling-project/docling-layout-heron", progress_callback)
        manager.download_hf_model("docling-project/docling-models", progress_callback)
        downloaded = True

    if vlm:
        console.print("[bold]Downloading VLM model (this may take a while)...[/bold]")
        manager.download_hf_model("ibm-granite/granite-vision-3.1-2b-preview", progress_callback)
        downloaded = True

    if easyocr or easyocr_lang:
        languages = list(easyocr_lang) if easyocr_lang else ["en", "ar"]
        console.print(f"[bold]Downloading EasyOCR models for {languages}...[/bold]")
        manager.download_easyocr_model(languages, progress_callback)
        downloaded = True

    if not downloaded:
        # Download required by default
        console.print("[bold]Downloading required models...[/bold]")
        results = manager.download_required(progress_callback=progress_callback)
        success_count = sum(1 for v in results.values() if v)
        console.print(f"[green]Downloaded {success_count}/{len(results)} required models[/green]")


@models.command("copy-from-cache")
def copy_from_cache():
    """Copy models from system cache (~/.cache) to ./models directory."""
    from .model_manager import ModelManager

    manager = ModelManager()

    console.print(f"[bold]Copying models to: {manager.models_dir}[/bold]")
    console.print()

    def progress_callback(msg):
        console.print(msg)

    results = manager.copy_from_cache(progress_callback=progress_callback)

    success_count = sum(1 for v in results.values() if v)
    console.print()
    console.print(f"[green]Copied {success_count}/{len(results)} items[/green]")


@models.command("status")
@click.option(
    "-o", "--output",
    default=None,
    type=click.Path(),
    help="Models directory to check",
)
def status(output):
    """Show status of downloaded models."""
    from .model_manager import ModelManager

    manager = ModelManager(models_dir=output)
    statuses = manager.get_model_status()

    console.print(f"[bold]Models directory: {manager.models_dir}[/bold]")
    console.print()

    # Create rich table
    table = Table(title="Model Status")
    table.add_column("Model", style="cyan")
    table.add_column("Status", style="green")
    table.add_column("Size", justify="right")
    table.add_column("Required", justify="center")

    for s in statuses:
        status_str = "[green]Ready[/green]" if s.downloaded else "[red]Missing[/red]"
        required_str = "[yellow]Yes[/yellow]" if s.required else "No"
        table.add_row(s.name, status_str, f"{s.size_mb}MB", required_str)

    console.print(table)

    # Disk usage
    usage = manager.get_disk_usage()
    console.print()
    console.print(f"Disk usage:")
    console.print(f"  HuggingFace: {usage['huggingface'] / 1024 / 1024:.1f} MB")
    console.print(f"  EasyOCR: {usage['easyocr'] / 1024 / 1024:.1f} MB")
    console.print(f"  Total: {usage['total'] / 1024 / 1024:.1f} MB")

    # Summary
    console.print()
    ready_count = sum(1 for s in statuses if s.downloaded)
    required_ready = sum(1 for s in statuses if s.downloaded and s.required)
    required_total = sum(1 for s in statuses if s.required)

    console.print(f"Total: {ready_count}/{len(statuses)} models ready")
    console.print(f"Required: {required_ready}/{required_total} ready")

    if manager.is_offline_mode():
        console.print("[yellow]Offline mode is enabled[/yellow]")


@models.command("clear")
@click.confirmation_option(prompt="Are you sure you want to clear the model cache?")
def clear():
    """Clear the model cache."""
    from .model_manager import ModelManager

    manager = ModelManager()

    if manager.clear_cache():
        console.print("[green]Cache cleared successfully[/green]")
    else:
        console.print("[red]Failed to clear cache[/red]")


@cli.command("setup-offline")
@click.option(
    "--include-optional",
    is_flag=True,
    help="Also download optional models (VLM, EasyOCR)",
)
def setup_offline(include_optional: bool):
    """Download all required models and configure for offline use.

    This downloads models to ./models and ensures the app can run
    fully offline. Run this once before using serve or serve-app.
    """
    from .config import disable_offline_mode, enable_offline_mode
    from .model_manager import ModelManager

    # Disable offline mode for downloads
    disable_offline_mode()

    manager = ModelManager()
    console.print(f"[bold]Models directory: {manager.models_dir}[/bold]")
    console.print()

    def progress_callback(msg):
        console.print(f"  {msg}")

    # Step 1: Try to copy from system cache first
    console.print("[bold]Step 1: Copying models from system cache...[/bold]")
    copy_results = manager.copy_from_cache(progress_callback=progress_callback)
    if copy_results:
        copied = sum(1 for v in copy_results.values() if v)
        console.print(f"[green]  Copied {copied}/{len(copy_results)} items from cache[/green]")
    else:
        console.print("  No cached models found")
    console.print()

    # Step 2: Download any missing required models
    console.print("[bold]Step 2: Downloading required models...[/bold]")
    results = manager.download_all(
        include_optional=include_optional,
        progress_callback=progress_callback,
    )
    success_count = sum(1 for v in results.values() if v)
    console.print(f"[green]  {success_count}/{len(results)} models ready[/green]")
    console.print()

    # Step 3: Verify all required models are available
    console.print("[bold]Step 3: Verifying models...[/bold]")
    statuses = manager.get_model_status()
    all_required_ready = True
    for s in statuses:
        status_str = "[green]Ready[/green]" if s.downloaded else "[red]Missing[/red]"
        marker = "[yellow]*[/yellow]" if s.required else " "
        console.print(f"  {marker} {s.name}: {status_str}")
        if s.required and not s.downloaded:
            all_required_ready = False

    console.print()
    if all_required_ready:
        console.print("[green bold]All required models are ready! You can now run offline.[/green bold]")
        console.print(f"  Start the app: [cyan]docling-playground serve-app[/cyan]")
    else:
        console.print("[red bold]Some required models are missing.[/red bold]")
        console.print("  Check your internet connection and try again.")

    # Re-enable offline mode
    enable_offline_mode()


@cli.command("serve")
@click.option(
    "--host",
    default="0.0.0.0",
    help="Server host address",
    show_default=True,
)
@click.option(
    "--port",
    default=8000,
    type=int,
    help="Server port",
    show_default=True,
)
@click.option(
    "--build",
    is_flag=True,
    help="Build frontend before serving",
)
@click.option(
    "--dev",
    is_flag=True,
    help="Run in development mode (auto-reload)",
)
def serve_app(host: str, port: int, build: bool, dev: bool):
    """Start the FastAPI + React playground server."""
    import subprocess
    import uvicorn
    from pathlib import Path

    frontend_dir = Path(__file__).parent.parent / "frontend"
    dist_dir = frontend_dir / "dist"

    # Build frontend if requested or if dist doesn't exist
    needs_build = build or not dist_dir.exists()

    if needs_build:
        if not frontend_dir.exists():
            console.print("[red]Frontend directory not found![/red]")
            console.print("Make sure you have the frontend/ directory with package.json")
            return

        if not (frontend_dir / "node_modules").exists():
            console.print("[yellow]Installing frontend dependencies...[/yellow]")
            result = subprocess.run(
                ["npm", "install"],
                cwd=str(frontend_dir),
                capture_output=True,
                text=True,
            )
            if result.returncode != 0:
                console.print(f"[red]npm install failed:[/red] {result.stderr}")
                return

        console.print("[yellow]Building frontend...[/yellow]")
        result = subprocess.run(
            ["npm", "run", "build"],
            cwd=str(frontend_dir),
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            console.print(f"[red]Build failed![/red]")
            if result.stdout:
                console.print(result.stdout)
            if result.stderr:
                console.print(result.stderr)
            return
        console.print("[green]Frontend built successfully![/green]")

    console.print(f"[green]Starting Docling Playground on {host}:{port}[/green]")
    console.print(f"[blue]Open http://localhost:{port} in your browser[/blue]")

    uvicorn.run("api.main:app", host=host, port=port, reload=dev)


@cli.command()
@click.argument("file", type=click.Path(exists=True))
@click.option(
    "--output", "-o",
    type=click.Choice(["markdown", "json", "summary"]),
    default="markdown",
    help="Output format",
)
@click.option(
    "--ocr/--no-ocr",
    default=True,
    help="Enable/disable OCR",
)
@click.option(
    "--ocr-library",
    type=click.Choice(["rapidocr", "easyocr", "tesseract"]),
    default="easyocr",
    help="OCR library to use",
)
def process(file, output, ocr, ocr_library):
    """Process a document from the command line."""
    from .config import Accelerator, OCRLibrary, OutputFormat, PipelineType
    from .models import ProcessingOptions
    from .processor import DocumentProcessor

    console.print(f"[bold]Processing {file}...[/bold]")

    options = ProcessingOptions(
        pipeline=PipelineType.STANDARD,
        accelerator=Accelerator.AUTO,
        ocr_enabled=ocr,
        ocr_library=OCRLibrary(ocr_library),
        output_format=OutputFormat(output),
    )

    processor = DocumentProcessor()
    result = processor.process_file(file, options)

    if not result.success:
        console.print(f"[red]Error: {result.error}[/red]")
        return

    # Display timing
    if result.timing:
        console.print(f"[green]Processed in {result.timing.total_seconds:.2f}s[/green]")

    # Display output based on format
    if output == "markdown":
        # Use print with errors='replace' to handle Unicode on Windows
        try:
            console.print(result.markdown)
        except UnicodeEncodeError:
            print(result.markdown.encode('utf-8', errors='replace').decode('utf-8'))
    elif output == "json":
        import json
        console.print(json.dumps(result.json_data, indent=2, ensure_ascii=False))
    else:  # summary
        console.print(f"Pages: {result.stats.num_pages}")
        console.print(f"Tables: {result.stats.num_tables}")
        console.print(f"Figures: {result.stats.num_figures}")
        console.print(f"Chunks: {result.stats.num_chunks}")
        console.print(f"Total Tokens: {result.stats.total_tokens}")


if __name__ == "__main__":
    cli()

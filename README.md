# Docling Playground

Interactive Docling document processing playground with a Gradio-based UI for experimenting with document processing parameters.

## Features

- **Interactive Parameter Configuration**: Adjust processing options in real-time
- **Multiple OCR Engines**: Choose between RapidOCR, EasyOCR, and Tesseract
- **Pipeline Selection**: Standard or VLM (Vision-Language Model) pipelines
- **Result Visualization**: Side-by-side, Markdown, JSON, and Chunks views
- **Processing Time Tracking**: Detailed timing breakdown for each processing stage
- **Model Management**: Download and manage models for offline use
- **Offline Mode**: Run completely offline with local models

## Installation

```bash
# Basic installation
pip install -e .

# With all OCR engines
pip install -e ".[ocr]"

# With Tesseract support
pip install -e ".[tesseract]"

# With GPU support
pip install -e ".[gpu]"

# With VLM support
pip install -e ".[vlm]"

# Everything
pip install -e ".[all]"
```

## Quick Start

### 1. Download Models

```bash
# Download all models to ./models directory
docling-playground models download --all

# Or copy from existing cache
docling-playground models copy-from-cache
```

### 2. Launch the Playground

```bash
# Start the Gradio server
docling-playground serve

# Run in offline mode (recommended for production)
docling-playground serve --offline

# With custom port
docling-playground serve --port 8080
```

Then open your browser to `http://localhost:7860`

---

## Processing Parameters Guide

### Pipeline

| Option | Description |
|--------|-------------|
| **standard** | Fast and reliable pipeline for most documents. Uses traditional ML models for layout analysis. |
| **vlm** | Vision-Language Model pipeline. Better for complex documents but requires more resources (~5GB model). |

**When to use VLM:**
- Complex multi-column layouts
- Documents with mixed content (tables, figures, text)
- When standard pipeline misses content

### Accelerator

| Option | Description |
|--------|-------------|
| **auto** | Automatically detect and use best available hardware (recommended) |
| **cpu** | Force CPU processing (slower but always available) |
| **cuda** | Use NVIDIA GPU (requires CUDA-enabled GPU) |
| **mps** | Use Apple Silicon GPU (Mac M1/M2/M3) |

### OCR Settings

#### Enable OCR
- **On**: Extract text from images and scanned documents
- **Off**: Only extract native text (faster for digital PDFs)

#### OCR Library

| Library | Speed | Accuracy | Languages | GPU Support | Best For |
|---------|-------|----------|-----------|-------------|----------|
| **RapidOCR** | Fast | Good | Limited (en, ch, ja, ko) | No | Quick processing, Asian languages |
| **EasyOCR** | Medium | Very Good | 80+ languages | Yes | Multi-language, Arabic, accuracy |
| **Tesseract** | Slow | Good | 100+ languages | No | Maximum language coverage |

#### Languages
Select the language(s) present in your document. Multi-select for mixed-language documents.

**EasyOCR Languages:**
- `en` - English
- `ar` - Arabic
- `zh_sim` - Chinese Simplified
- `zh_tra` - Chinese Traditional
- `ja` - Japanese
- `ko` - Korean
- `fr` - French
- `de` - German
- `es` - Spanish
- `ru` - Russian
- And many more...

#### Force Full Page OCR
- **Off** (default): OCR only detected text regions (faster)
- **On**: OCR the entire page (use for scanned documents or poor quality PDFs)

### Advanced Features

#### Table Structure Extraction
- **On** (default): Detect and extract table structure with cells and headers
- **Off**: Treat tables as regular text

#### Code Enrichment
- **On**: Detect and format code blocks with syntax highlighting
- **Off**: Treat code as regular text

#### Formula Enrichment
- **On**: Detect and extract mathematical formulas (LaTeX)
- **Off**: Treat formulas as regular text

#### Picture Description (VLM)
- **On**: Generate descriptions for images using Vision-Language Model
- **Off**: Just detect images without descriptions
- **Note**: Requires VLM model (~5GB)

### Output Settings

#### Output Format

| Format | Description |
|--------|-------------|
| **markdown** | Human-readable Markdown with formatting preserved |
| **json** | Full DoclingDocument structure for programmatic access |
| **summary** | Metadata and statistics only |

#### Chunk Max Tokens
Control the maximum size of text chunks for RAG (Retrieval-Augmented Generation):
- **128-256**: Smaller chunks, more precise retrieval
- **512** (default): Balanced for most use cases
- **1024-2048**: Larger chunks, more context per chunk

---

## Model Management

### Models Directory Structure

```
./models/                          (~50 GB total)
├── huggingface/hub/
│   ├── models--docling-project--docling-layout-heron/   (~164 MB)
│   ├── models--docling-project--docling-models/         (~342 MB)
│   └── models--ibm-granite--granite-vision-3.1-2b-preview/  (~5 GB)
├── easyocr/
│   ├── craft_mlt_25k.pth         (detector, ~80 MB)
│   ├── english_g2.pth            (~15 MB)
│   └── arabic.pth                (~206 MB)
└── rapidocr/
```

### CLI Commands

```bash
# Check model status
docling-playground models status

# Download all models
docling-playground models download --all

# Download specific components
docling-playground models download --docling      # Core Docling models (~500 MB)
docling-playground models download --vlm          # Vision-Language Model (~5 GB)
docling-playground models download --easyocr      # EasyOCR (en + ar, ~300 MB)

# Download specific EasyOCR languages
docling-playground models download --easyocr-lang en --easyocr-lang ar --easyocr-lang fr

# Copy from system cache to ./models
docling-playground models copy-from-cache

# Clear models
docling-playground models clear
```

---

## CLI Processing

Process documents directly from the command line:

```bash
# Basic processing
docling-playground process document.pdf

# With specific options
docling-playground process document.pdf \
    --output markdown \
    --ocr-library easyocr

# Without OCR (for digital PDFs)
docling-playground process document.pdf --no-ocr

# Output formats
docling-playground process document.pdf -o json      # Full JSON
docling-playground process document.pdf -o markdown  # Markdown
docling-playground process document.pdf -o summary   # Stats only
```

---

## Python API Usage

```python
from src.processor import DocumentProcessor
from src.models import ProcessingOptions
from src.config import PipelineType, Accelerator, OCRLibrary, OutputFormat

# Create processor
processor = DocumentProcessor()

# Configure options
options = ProcessingOptions(
    pipeline=PipelineType.STANDARD,
    accelerator=Accelerator.AUTO,
    ocr_enabled=True,
    ocr_library=OCRLibrary.EASYOCR,
    ocr_languages=["en", "ar"],
    force_full_page_ocr=False,
    do_table_structure=True,
    do_code_enrichment=False,
    do_formula_enrichment=False,
    do_picture_description=False,
    output_format=OutputFormat.MARKDOWN,
    chunk_max_tokens=512,
)

# Process document
result = processor.process_file("document.pdf", options)

# Access results
if result.success:
    print(f"Processed in {result.timing.total_seconds:.2f}s")
    print(f"Pages: {result.stats.num_pages}")
    print(f"Tables: {result.stats.num_tables}")
    print(f"Chunks: {len(result.chunks)}")

    # Get markdown output
    print(result.markdown)

    # Get JSON output
    print(result.json_data)

    # Access chunks
    for chunk in result.chunks:
        print(f"Chunk {chunk.index}: {chunk.preview}")
else:
    print(f"Error: {result.error}")
```

---

## Offline Deployment

### Prepare for Offline Use

1. Download all models:
   ```bash
   docling-playground models download --all
   ```

2. Verify models:
   ```bash
   docling-playground models status
   ```

3. Test offline mode:
   ```bash
   docling-playground serve --offline
   ```

### Deploy to Another Machine

1. Copy the entire project including `./models` folder
2. Install dependencies:
   ```bash
   pip install -e .
   ```
3. Run in offline mode:
   ```bash
   docling-playground serve --offline
   ```

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `HF_HOME` | HuggingFace cache directory | `./models/huggingface` |
| `HF_HUB_OFFLINE` | Disable HuggingFace downloads | `0` |
| `EASYOCR_MODULE_PATH` | EasyOCR models directory | `./models/easyocr` |

---

## Supported File Formats

| Format | Extensions | Notes |
|--------|------------|-------|
| PDF | `.pdf` | Best support, native + scanned |
| Word | `.docx` | Microsoft Word documents |
| PowerPoint | `.pptx` | Microsoft PowerPoint |
| HTML | `.html`, `.htm` | Web pages |
| Images | `.png`, `.jpg`, `.jpeg`, `.tiff`, `.bmp` | Requires OCR |

---

## Performance Tips

1. **For digital PDFs**: Disable OCR for faster processing
2. **For scanned documents**: Enable "Force Full Page OCR"
3. **For multi-language docs**: Select all relevant languages in OCR settings
4. **For large documents**: Use RapidOCR (faster) over EasyOCR
5. **For accuracy**: Use EasyOCR with GPU acceleration
6. **For Arabic/RTL**: Use EasyOCR with Arabic model

---

## Troubleshooting

### Models not found
```bash
# Re-download models
docling-playground models download --all
```

### Out of memory
- Use `cpu` accelerator instead of `cuda`
- Disable VLM features
- Process smaller documents

### Slow processing
- Disable OCR for digital PDFs
- Use RapidOCR instead of EasyOCR
- Use `cuda` accelerator if GPU available

### Arabic text not recognized
```bash
# Download Arabic EasyOCR model
docling-playground models download --easyocr-lang ar
```

---

## License

MIT License

## Links

- [Docling Documentation](https://docling-project.github.io/docling/)
- [Docling GitHub](https://github.com/docling-project/docling)
- [Gradio Documentation](https://www.gradio.app/docs)

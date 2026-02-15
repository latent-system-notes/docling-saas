# Docling-Serve: Offline Deployment on NVIDIA DGX Spark

> Build on Windows (with internet) → Deploy on DGX Spark (offline)
>
> Full Arabic + English OCR + VLM Picture Description support

---

## Table of Contents

1. [Overview](#1-overview)
2. [Prerequisites](#2-prerequisites)
3. [Project Structure](#3-project-structure)
4. [Step 1: Create Dockerfile](#4-step-1-create-dockerfile)
5. [Step 2: Setup Docker Buildx for ARM64](#5-step-2-setup-docker-buildx-for-arm64)
6. [Step 3: Build ARM64 Docker Image](#6-step-3-build-arm64-docker-image)
7. [Step 4: Download AI Models](#7-step-4-download-ai-models)
8. [Step 5: Download EasyOCR Arabic Models](#8-step-5-download-easyocr-arabic-models)
9. [Step 6: Download VLM Models](#9-step-6-download-vlm-models)
10. [Step 7: Package Everything for Transfer](#10-step-7-package-everything-for-transfer)
11. [Step 8: Deploy on DGX Spark](#11-step-8-deploy-on-dgx-spark)
12. [Step 9: Verify & Test](#12-step-9-verify--test)
13. [API Usage Examples](#13-api-usage-examples)
14. [Model Reference](#14-model-reference)
15. [Troubleshooting](#15-troubleshooting)

---

## 1. Overview

### Architecture

```
┌──────────────────────┐         USB/SSD         ┌──────────────────────┐
│    Windows PC        │ ──────────────────────── │    DGX Spark         │
│    (x86_64)          │     Transfer files       │    (ARM64)           │
│    Internet ✓        │                          │    Offline ✗         │
│                      │                          │    128 GB Unified    │
│  • Build ARM64 image │                          │    Grace Blackwell   │
│  • Download models   │                          │                      │
└──────────────────────┘                          └──────────────────────┘
```

### What Gets Built

| Component | Built Where | Size (approx) |
|-----------|-------------|---------------|
| Docker image (no models) | Windows → ARM64 cross-build | ~15-18 GB |
| Docling core models | Windows download | ~1.5 GB |
| EasyOCR Arabic models | Windows download | ~300 MB |
| VLM models (picture description) | Windows download | ~6 GB |
| **Total transfer** | | **~23-26 GB** |

### Capabilities After Deployment

- PDF/DOCX/HTML/image conversion with full structure extraction
- Arabic + English OCR (EasyOCR and Tesseract)
- Table structure recognition (TableFormer)
- Picture classification and description (SmolVLM, Granite-Vision)
- Code and formula extraction
- Fully offline — zero internet required at runtime

---

## 2. Prerequisites

### On Windows

- **Docker Desktop** (v4.20+) with WSL2 backend enabled
- **Python 3.10+** (for downloading models)
- **~60 GB free disk space** (for build + models + tar)
- **USB drive or external SSD** (32+ GB) for transferring to Spark

### On DGX Spark

- **DGX OS** (pre-installed)
- **Docker** with NVIDIA Container Runtime (pre-installed)
- **~35 GB free disk space** for the image + models

---

## 3. Project Structure

Create a project folder on Windows:

```
C:\docling-spark\
├── Dockerfile              # ARM64 base image (no models)
├── download_models.py      # Script to download all AI models
├── models\                 # Downloaded models (created by script)
│   ├── docling-artifacts\  # Docling core models
│   ├── easyocr\            # EasyOCR models (Arabic + English)
│   └── huggingface\        # VLM models for picture description
└── output\                 # Final tar files for transfer
    ├── docling-serve-arm64.tar
    └── models\             # Copy of models folder
```

Open PowerShell and create the structure:

```powershell
mkdir C:\docling-spark
mkdir C:\docling-spark\models
mkdir C:\docling-spark\models\docling-artifacts
mkdir C:\docling-spark\models\easyocr
mkdir C:\docling-spark\models\huggingface
mkdir C:\docling-spark\output
cd C:\docling-spark
```

---

## 4. Step 1: Create Dockerfile

Create `C:\docling-spark\Dockerfile` with the following content.

This Dockerfile builds the base image **without** models — models will be mounted
as volumes at runtime on the Spark, keeping the image smaller and models easy to update.

```dockerfile
FROM nvcr.io/nvidia/pytorch:26.01-py3

# ============================================================
# System Dependencies: Tesseract OCR (Arabic + English)
# ============================================================
RUN apt-get update && apt-get install -y --no-install-recommends \
    tesseract-ocr \
    tesseract-ocr-eng \
    tesseract-ocr-ara \
    tesseract-ocr-osd \
    libtesseract-dev \
    libleptonica-dev \
    pkg-config \
    libgl1-mesa-glx \
    libglib2.0-0 \
    build-essential \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# ============================================================
# Environment Variables
# ============================================================
ENV TESSDATA_PREFIX=/usr/share/tesseract-ocr/5/tessdata/
ENV DOCLING_ARTIFACTS_PATH=/root/.cache/docling/models
ENV DOCLING_DEVICE=cuda
ENV EASYOCR_MODULE_PATH=/root/.EasyOCR

# ============================================================
# Protect NVIDIA's pre-installed PyTorch
#
# CRITICAL: docling-serve depends on torch. If we don't pin
# the NVIDIA version, pip will overwrite it with a generic
# PyTorch wheel that does NOT have CUDA support for ARM64.
# ============================================================
RUN pip freeze | grep -iE "^(torch|torchvision|torchaudio|nvidia)" \
    > /tmp/nvidia-pins.txt && \
    echo "=== Pinned NVIDIA packages ===" && \
    cat /tmp/nvidia-pins.txt

# ============================================================
# Disable NVIDIA's pip constraints file
#
# Since release 25.03, NVIDIA containers include
# /etc/pip/constraint.txt which locks specific library
# versions. This can conflict with docling-serve's
# dependencies, so we back it up and clear it.
# ============================================================
RUN if [ -f /etc/pip/constraint.txt ]; then \
      cp /etc/pip/constraint.txt /etc/pip/constraint.txt.bak && \
      echo "" > /etc/pip/constraint.txt && \
      echo "Constraints file backed up and cleared"; \
    else \
      echo "No constraints file found"; \
    fi

# ============================================================
# Install docling-serve with UI
#
# The -c flag tells pip to keep the NVIDIA PyTorch packages
# at their current versions and not downgrade/replace them.
# ============================================================
RUN pip install --no-cache-dir -c /tmp/nvidia-pins.txt "docling-serve[ui]"

# ============================================================
# Verify PyTorch was NOT overwritten
# ============================================================
RUN python -c "\
import torch; \
print(f'PyTorch version: {torch.__version__}'); \
print(f'CUDA available:  {torch.cuda.is_available()}'); \
print(f'CUDA version:    {torch.version.cuda}'); \
print('Verification PASSED' if torch.cuda.is_available() else 'WARNING: CUDA not available (expected during cross-build)') \
"

# ============================================================
# Set offline mode
#
# These environment variables prevent HuggingFace and
# Transformers from attempting any downloads at runtime.
# Models must be pre-downloaded and mounted as volumes.
# ============================================================
ENV HF_HUB_OFFLINE=1
ENV TRANSFORMERS_OFFLINE=1

# ============================================================
# Expose and configure
# ============================================================
EXPOSE 5001
ENV DOCLING_SERVE_ENABLE_UI=true

CMD ["docling-serve", "run", "--host", "0.0.0.0", "--port", "5001"]
```

> **Note on CUDA verification:** During cross-build (QEMU emulation on Windows),
> `torch.cuda.is_available()` will return `False` because there is no GPU in the
> build environment. This is expected. CUDA will work correctly when running on
> the actual DGX Spark hardware.

---

## 5. Step 2: Setup Docker Buildx for ARM64

Docker Desktop includes buildx and QEMU support. We need to create a builder
instance that can cross-compile for ARM64 (aarch64).

```powershell
# Create a new buildx builder
docker buildx create --name sparkbuilder --use

# Bootstrap the builder (downloads QEMU if needed)
docker buildx inspect --bootstrap
```

Verify ARM64 support is available:

```powershell
docker buildx ls
```

You should see `linux/arm64` in the list of supported platforms. Example output:

```
sparkbuilder  docker-container
  sparkbuilder0  sparkbuilder0  running  linux/amd64, linux/arm64, linux/arm/v7, ...
```

If `linux/arm64` is not listed, ensure Docker Desktop is up to date and WSL2
integration is enabled in Docker Desktop settings.

---

## 6. Step 3: Build ARM64 Docker Image

This step cross-compiles the Docker image for ARM64. It uses QEMU emulation
under the hood, so it will be slower than a native build.

```powershell
cd C:\docling-spark

# Build for ARM64 and export as tar file
docker buildx build --platform linux/arm64 ^
    -t docling-serve:latest ^
    --output type=docker,dest=output\docling-serve-arm64.tar ^
    .
```

### Expected behavior

- **Duration:** 30-90 minutes depending on your PC and internet speed
- **Disk usage:** The tar file will be approximately 15-18 GB
- **Network:** Downloads the NVIDIA base image (~14 GB) and Python packages
- **CPU:** QEMU emulation is CPU-intensive; expect high CPU usage

### If the build fails

Common issues and solutions:

| Error | Cause | Solution |
|-------|-------|---------|
| `no match for platform` | Base image doesn't have ARM64 variant | Check that `26.01-py3` is available (not `-igpu`) |
| `pip install` timeout | Large packages timeout during QEMU emulation | Add `--network=host` to the build command |
| Out of disk space | Need ~60 GB free during build | Free up space or change Docker's data directory |
| QEMU crashes | Memory limit | Increase WSL2 memory in `.wslconfig` |

**To increase WSL2 memory**, create or edit `C:\Users\<YOU>\.wslconfig`:

```ini
[wsl2]
memory=16GB
swap=8GB
```

Then restart WSL2: `wsl --shutdown`

---

## 7. Step 4: Download AI Models (Docling Core)

These are the core models for layout detection, table structure, picture
classification, and code/formula extraction. They are platform-independent
(just weight files), so downloading on Windows is fine.

### Install Python dependencies (temporary, on Windows)

```powershell
# Create a virtual environment (recommended)
python -m venv C:\docling-spark\venv
C:\docling-spark\venv\Scripts\activate

# Install docling tools
pip install docling
```

### Download models

```powershell
python -c "
from pathlib import Path
from docling.utils.model_downloader import download_models

output = Path(r'C:\docling-spark\models\docling-artifacts')

download_models(
    output_dir=output,
    with_layout=True,
    with_tableformer=True,
    with_picture_classifier=True,
    with_code_formula=True,
    with_easyocr=True,
)
print('All Docling core models downloaded successfully')
"
```

### Verify download

```powershell
dir C:\docling-spark\models\docling-artifacts
```

You should see folders/files for layout models, TableFormer, EasyOCR, etc.

---

## 8. Step 5: Download EasyOCR Arabic Models

The default Docling download only includes English + Latin EasyOCR models.
Arabic must be downloaded separately.

```powershell
# Make sure you're in the venv
C:\docling-spark\venv\Scripts\activate

pip install easyocr

python -c "
import easyocr
import shutil
from pathlib import Path

# This triggers download of Arabic + English models
print('Downloading EasyOCR Arabic + English models...')
reader = easyocr.Reader(['ar', 'en'], gpu=False, download_enabled=True)
print('Download complete')

# Copy models to our models folder
import os
easyocr_home = os.path.expanduser('~/.EasyOCR/model')
dest = Path(r'C:\docling-spark\models\easyocr')

for f in os.listdir(easyocr_home):
    src = os.path.join(easyocr_home, f)
    dst = dest / f
    if os.path.isfile(src):
        shutil.copy2(src, dst)
        print(f'  Copied: {f} ({os.path.getsize(src) / 1024 / 1024:.1f} MB)')

print('EasyOCR models copied successfully')
"
```

### Verify download

```powershell
dir C:\docling-spark\models\easyocr
```

Expected files:

| File | Size | Purpose |
|------|------|---------|
| `craft_mlt_25k.pth` | ~83 MB | Text detection (all languages) |
| `english_g2.pth` | ~15 MB | English recognition |
| `latin_g2.pth` | ~15 MB | Latin script recognition |
| `arabic.pth` | ~215 MB | Arabic recognition |

---

## 9. Step 6: Download VLM Models (Picture Description)

These Vision-Language Models enable docling to generate descriptions of
images/figures found in documents.

```powershell
# Make sure you're in the venv
C:\docling-spark\venv\Scripts\activate

pip install huggingface-hub

python -c "
from huggingface_hub import snapshot_download
import os

base = r'C:\docling-spark\models\huggingface'

models = [
    {
        'repo': 'HuggingFaceTB/SmolVLM-256M-Instruct',
        'desc': 'SmolVLM 256M - lightweight picture description (default)',
        'size': '~500 MB',
    },
    {
        'repo': 'ibm-granite/granite-vision-3.3-2b',
        'desc': 'Granite Vision 3.3 2B - detailed picture description',
        'size': '~4 GB',
    },
    {
        'repo': 'ibm-granite/granite-docling-258M',
        'desc': 'Granite Docling 258M - code/formula + VLM convert',
        'size': '~500 MB',
    },
    {
        'repo': 'ds4sd/SmolDocling-256M-preview',
        'desc': 'SmolDocling 256M - alternative VLM convert',
        'size': '~500 MB',
    },
]

for m in models:
    repo = m['repo']
    name = repo.split('/')[-1]
    local_dir = os.path.join(base, name)
    print(f'')
    print(f'Downloading: {repo}')
    print(f'Description: {m[\"desc\"]}')
    print(f'Est. size:   {m[\"size\"]}')
    print(f'Saving to:   {local_dir}')
    print(f'---')
    snapshot_download(repo, local_dir=local_dir)
    print(f'Done: {repo}')

print('')
print('All VLM models downloaded successfully!')
"
```

### Verify download

```powershell
dir C:\docling-spark\models\huggingface
```

Expected folders:

```
C:\docling-spark\models\huggingface\
├── SmolVLM-256M-Instruct\       (~500 MB)
├── granite-vision-3.3-2b\       (~4 GB)
├── granite-docling-258M\        (~500 MB)
└── SmolDocling-256M-preview\    (~500 MB)
```

### Optional: Skip large models

If disk space or transfer time is a concern, you can skip `granite-vision-3.3-2b`
(the largest at ~4 GB). SmolVLM-256M alone is sufficient for basic picture
descriptions. To skip it, remove it from the `models` list in the script above.

---

## 10. Step 7: Package Everything for Transfer

### Final output structure

```powershell
dir C:\docling-spark\output\
```

Should contain:

```
C:\docling-spark\output\
├── docling-serve-arm64.tar      (Docker image, ~15-18 GB)
└── (models will be copied next)
```

### Copy models to output folder

```powershell
xcopy /E /I C:\docling-spark\models C:\docling-spark\output\models
```

### Verify everything is present

```powershell
# Check Docker image tar
dir C:\docling-spark\output\docling-serve-arm64.tar

# Check models
dir C:\docling-spark\output\models\docling-artifacts
dir C:\docling-spark\output\models\easyocr
dir C:\docling-spark\output\models\huggingface
```

### Copy to USB / External SSD

```powershell
# Replace E:\ with your USB drive letter
xcopy /E /I C:\docling-spark\output E:\docling-spark
```

### Summary of files to transfer

| Path on USB | Contents | Size |
|-------------|----------|------|
| `docling-serve-arm64.tar` | Docker image (ARM64, no models) | ~15-18 GB |
| `models\docling-artifacts\` | Layout, TableFormer, OCR, Code/Formula | ~1.5 GB |
| `models\easyocr\` | Arabic + English OCR weights | ~300 MB |
| `models\huggingface\` | SmolVLM, Granite-Vision, Granite-Docling, SmolDocling | ~6 GB |
| **Total** | | **~23-26 GB** |

---

## 11. Step 8: Deploy on DGX Spark

### Copy files from USB to Spark

Plug the USB drive into the DGX Spark and copy files:

```bash
# Find the USB mount point
lsblk
# Usually at /media/<user>/<drive-name> or similar

# Create working directory
mkdir -p /home/$USER/docling
cd /home/$USER/docling

# Copy from USB (adjust path as needed)
cp /media/$USER/USB_DRIVE/docling-spark/docling-serve-arm64.tar .
cp -r /media/$USER/USB_DRIVE/docling-spark/models .
```

### Load Docker image

```bash
docker load -i docling-serve-arm64.tar
```

This may take a few minutes. When complete, verify:

```bash
docker images | grep docling-serve
```

Expected output:

```
docling-serve   latest   abc123def456   ...   15.2GB
```

### Create a run script

Create `/home/$USER/docling/run.sh`:

```bash
#!/bin/bash

# ============================================================
# Docling-Serve Launcher for DGX Spark (Offline)
# ============================================================

MODELS_DIR="/home/$USER/docling/models"

docker run --gpus=all \
    --shm-size=16g \
    -p 5001:5001 \
    -v ${MODELS_DIR}/docling-artifacts:/root/.cache/docling/models \
    -v ${MODELS_DIR}/huggingface:/root/.cache/huggingface/hub \
    -v ${MODELS_DIR}/easyocr:/root/.EasyOCR/model \
    -e DOCLING_ARTIFACTS_PATH=/root/.cache/docling/models \
    -e EASYOCR_MODULE_PATH=/root/.EasyOCR \
    -e HF_HUB_OFFLINE=1 \
    -e TRANSFORMERS_OFFLINE=1 \
    -e DOCLING_DEVICE=cuda \
    docling-serve:latest
```

Make it executable:

```bash
chmod +x /home/$USER/docling/run.sh
```

### Start the server

```bash
cd /home/$USER/docling
./run.sh
```

The server will start and be available at:

| Endpoint | URL |
|----------|-----|
| API | `http://localhost:5001` |
| Swagger UI (API docs) | `http://localhost:5001/docs` |
| Web UI | `http://localhost:5001/ui` |

---

## 12. Step 9: Verify & Test

### Quick health check

```bash
curl http://localhost:5001/health
```

### Test basic conversion

```bash
curl -X 'POST' \
  'http://localhost:5001/v1/convert/source' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
    "options": {
      "to_formats": ["md"]
    },
    "sources": [{"kind": "http", "url": "https://arxiv.org/pdf/2501.17887"}]
  }'
```

> **Note:** Since the Spark is offline, use `"kind": "file"` with base64-encoded
> documents or mount a local folder with documents. See API examples below.

### Test with a local file

```bash
# Base64 encode a local PDF
BASE64=$(base64 -w 0 /path/to/document.pdf)

curl -X 'POST' \
  'http://localhost:5001/v1/convert/source' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d "{
    \"options\": {
      \"do_ocr\": true,
      \"ocr_engine\": \"easyocr\",
      \"ocr_lang\": [\"ar\", \"en\"],
      \"do_picture_description\": true,
      \"to_formats\": [\"md\", \"json\"]
    },
    \"sources\": [{
      \"kind\": \"file\",
      \"filename\": \"document.pdf\",
      \"base64_string\": \"${BASE64}\"
    }]
  }"
```

---

## 13. API Usage Examples

### Arabic Document with EasyOCR

```json
{
  "options": {
    "do_ocr": true,
    "ocr_engine": "easyocr",
    "ocr_lang": ["ar", "en"],
    "to_formats": ["md", "json"]
  },
  "sources": [{
    "kind": "file",
    "filename": "arabic_doc.pdf",
    "base64_string": "<base64>"
  }]
}
```

### Arabic Document with Tesseract

```json
{
  "options": {
    "do_ocr": true,
    "ocr_engine": "tesseract",
    "ocr_lang": ["ara", "eng"],
    "to_formats": ["md"]
  },
  "sources": [{
    "kind": "file",
    "filename": "arabic_doc.pdf",
    "base64_string": "<base64>"
  }]
}
```

> **Language codes differ:** EasyOCR uses `"ar"`, Tesseract uses `"ara"`.

### With Picture Description (SmolVLM — default)

```json
{
  "options": {
    "do_ocr": true,
    "ocr_engine": "easyocr",
    "ocr_lang": ["ar", "en"],
    "do_picture_description": true,
    "do_picture_classification": true,
    "to_formats": ["md", "json"]
  },
  "sources": [{
    "kind": "file",
    "filename": "report.pdf",
    "base64_string": "<base64>"
  }]
}
```

### With Picture Description (Granite-Vision — higher quality)

```json
{
  "options": {
    "do_ocr": true,
    "ocr_engine": "easyocr",
    "ocr_lang": ["ar", "en"],
    "do_picture_description": true,
    "picture_description_options": {
      "repo_id": "ibm-granite/granite-vision-3.3-2b",
      "prompt": "What is shown in this image? Describe in detail."
    },
    "to_formats": ["md", "json"]
  },
  "sources": [{
    "kind": "file",
    "filename": "report.pdf",
    "base64_string": "<base64>"
  }]
}
```

---

## 14. Model Reference

### Docling Core Models

| Model | HuggingFace Repo | Purpose |
|-------|-----------------|---------|
| Layout Heron | `ds4sd/docling-layout-heron` | Document structure detection (default) |
| TableFormer | `ds4sd/docling-models` | Table structure recognition |
| Picture Classifier | `ds4sd/DocumentFigureClassifier` | Classify 16 image types |
| Code Formula | `ds4sd/CodeFormula` | Extract code and math formulas |

### OCR Models

| Engine | Languages | Notes |
|--------|-----------|-------|
| EasyOCR | `["ar", "en"]` | Best for Arabic, deep learning based |
| Tesseract | `["ara", "eng"]` | Faster, needs clean scans |

### VLM Models (Picture Description)

| Model | Size | VRAM | Quality | Speed |
|-------|------|------|---------|-------|
| SmolVLM-256M ⭐ | 500 MB | ~1 GB | Basic (2-3 sentences) | Fast |
| Granite-Vision-3.3-2B | 4 GB | ~5 GB | Detailed & accurate | Medium |
| Granite-Docling-258M | 500 MB | ~1 GB | Code/formula focused | Fast |
| SmolDocling-256M | 500 MB | ~1 GB | Document conversion | Fast |

---

## 15. Troubleshooting

### Build Issues (Windows)

**QEMU crashes during build:**

```powershell
# Increase WSL2 memory
# Edit C:\Users\<YOU>\.wslconfig:
# [wsl2]
# memory=16GB
# swap=8GB

wsl --shutdown
# Then retry the build
```

**Build hangs at pip install:**

```powershell
# Try with increased timeout
docker buildx build --platform linux/arm64 ^
    --build-arg PIP_DEFAULT_TIMEOUT=300 ^
    -t docling-serve:latest ^
    --output type=docker,dest=output\docling-serve-arm64.tar ^
    .
```

**"no space left on device":**

```powershell
# Clean Docker cache
docker builder prune -a
docker system prune -a

# Move Docker data directory if needed (Docker Desktop Settings > Resources)
```

### Runtime Issues (DGX Spark)

**"CUDA not available":**

```bash
# Verify NVIDIA runtime is working
docker run --rm --gpus=all nvcr.io/nvidia/cuda:13.0.1-devel-ubuntu24.04 nvidia-smi

# If nvidia-smi works but docling doesn't see CUDA,
# PyTorch may have been overwritten during build.
# Check inside container:
docker run --rm --gpus=all docling-serve:latest \
    python -c "import torch; print(torch.cuda.is_available())"
```

**Models not found:**

```bash
# Verify volume mounts are correct
docker run --rm \
    -v /home/$USER/docling/models/docling-artifacts:/root/.cache/docling/models \
    docling-serve:latest \
    ls -la /root/.cache/docling/models/

# Verify EasyOCR Arabic model
docker run --rm \
    -v /home/$USER/docling/models/easyocr:/root/.EasyOCR/model \
    docling-serve:latest \
    ls -la /root/.EasyOCR/model/
```

**HuggingFace models not found at runtime:**

The HF models downloaded by `snapshot_download` follow a specific directory
structure. If docling can't find them, the mount path may need adjustment.

```bash
# Check what docling expects
docker run --rm docling-serve:latest \
    python -c "from huggingface_hub import scan_cache_dir; print(scan_cache_dir())"

# You may need to restructure the HF models to match:
# /root/.cache/huggingface/hub/models--<org>--<name>/
```

Alternative: mount models at a custom path and set the environment variable:

```bash
docker run --gpus=all --shm-size=16g \
    -p 5001:5001 \
    -v /home/$USER/docling/models/docling-artifacts:/root/.cache/docling/models \
    -v /home/$USER/docling/models/huggingface:/models/hf \
    -v /home/$USER/docling/models/easyocr:/root/.EasyOCR/model \
    -e DOCLING_ARTIFACTS_PATH=/root/.cache/docling/models \
    -e HF_HOME=/models/hf \
    -e HF_HUB_OFFLINE=1 \
    -e TRANSFORMERS_OFFLINE=1 \
    docling-serve:latest
```

**Server starts but API returns errors:**

```bash
# Check logs
docker logs <container_id>

# Run interactively to debug
docker run -it --gpus=all \
    -v /home/$USER/docling/models/docling-artifacts:/root/.cache/docling/models \
    -v /home/$USER/docling/models/huggingface:/root/.cache/huggingface/hub \
    -v /home/$USER/docling/models/easyocr:/root/.EasyOCR/model \
    -e HF_HUB_OFFLINE=1 \
    -e TRANSFORMERS_OFFLINE=1 \
    docling-serve:latest \
    bash

# Inside the container:
python -c "import docling; print(docling.__version__)"
python -c "import easyocr; r = easyocr.Reader(['ar','en'], gpu=True); print('OK')"
docling-serve run --host 0.0.0.0 --port 5001
```

---

## Notes

- **DGX Spark uses `--gpus=all`** (not `--runtime nvidia` which is for Jetson)
- **Container tag:** Use the standard `pytorch:26.01-py3` tag (not `-igpu`)
- **Model files are platform-independent** — weight files (ONNX, SafeTensors, .pth)
  work identically on x86_64 and ARM64
- **128 GB unified memory** on DGX Spark means all models can be loaded simultaneously
- **Memory bandwidth** (273 GB/s) is the main bottleneck, not memory capacity;
  batch processing (like document conversion) is not significantly affected

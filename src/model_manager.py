"""Model download and offline management."""

import os
import shutil
from pathlib import Path

from .config import (
    MODELS_DIR,
    HUGGINGFACE_MODELS_DIR,
    EASYOCR_MODELS_DIR,
    MODELS_INFO,
    OCRLibrary,
    is_offline_mode,
)
from .models import ModelStatus


class ModelManager:
    """Manages model downloads and offline mode."""

    def __init__(self, models_dir: str | Path | None = None):
        """Initialize model manager.

        Args:
            models_dir: Root path for models. Defaults to ./models in project directory.
        """
        if models_dir:
            self.models_dir = Path(models_dir)
        else:
            self.models_dir = MODELS_DIR

        self.huggingface_dir = self.models_dir / "huggingface"
        self.easyocr_dir = self.models_dir / "easyocr"

        # Create directories
        self.models_dir.mkdir(parents=True, exist_ok=True)
        self.huggingface_dir.mkdir(parents=True, exist_ok=True)
        self.easyocr_dir.mkdir(parents=True, exist_ok=True)

        # For display in UI
        self.artifacts_path = str(self.models_dir)

    def setup_environment(self):
        """Set up environment variables to use local models."""
        os.environ["HF_HOME"] = str(self.huggingface_dir)
        os.environ["HF_HUB_CACHE"] = str(self.huggingface_dir / "hub")
        os.environ["TRANSFORMERS_CACHE"] = str(self.huggingface_dir / "transformers")
        os.environ["EASYOCR_MODULE_PATH"] = str(self.easyocr_dir)

    def _check_hf_model_exists(self, repo_id: str, subfolder: str | None = None) -> bool:
        """Check if a HuggingFace model is cached locally."""
        try:
            from huggingface_hub import scan_cache_dir

            # Check in local models directory
            hub_cache = self.huggingface_dir / "hub"
            if not hub_cache.exists():
                # Also check default HF cache
                default_cache = Path.home() / ".cache" / "huggingface" / "hub"
                if not default_cache.exists():
                    return False
                cache_info = scan_cache_dir(default_cache)
            else:
                cache_info = scan_cache_dir(hub_cache)

            for repo in cache_info.repos:
                if repo.repo_id == repo_id:
                    return repo.size_on_disk > 0
            return False
        except Exception:
            return False

    def _check_easyocr_model_exists(self, language: str | None = None) -> bool:
        """Check if EasyOCR model files exist."""
        # Check local easyocr directory first
        if self.easyocr_dir.exists():
            if language:
                model_files = list(self.easyocr_dir.glob(f"*{language}*"))
                if len(model_files) > 0:
                    return True

        # Also check default EasyOCR path
        default_path = Path.home() / ".EasyOCR" / "model"
        if default_path.exists():
            if language:
                model_files = list(default_path.glob(f"*{language}*"))
                return len(model_files) > 0
            return True

        return False

    def _check_ocr_model_exists(self, library: OCRLibrary, language: str | None = None) -> bool:
        """Check if OCR model files exist."""
        if library == OCRLibrary.EASYOCR:
            return self._check_easyocr_model_exists(language)

        elif library == OCRLibrary.RAPIDOCR:
            try:
                import rapidocr
                return True
            except ImportError:
                try:
                    import rapidocr_onnxruntime
                    return True
                except ImportError:
                    return False

        elif library == OCRLibrary.TESSERACT:
            tessdata = os.environ.get("TESSDATA_PREFIX", "/usr/share/tesseract-ocr/tessdata")
            if language:
                lang_file = Path(tessdata) / f"{language}.traineddata"
                return lang_file.exists()
            return Path(tessdata).exists()

        return False

    def get_model_status(self) -> list[ModelStatus]:
        """Get status of all models."""
        statuses = []

        for model_id, info in MODELS_INFO.items():
            downloaded = False
            path = None

            if info.get("hf_repo"):
                downloaded = self._check_hf_model_exists(
                    info["hf_repo"],
                    info.get("subfolder"),
                )
                if downloaded:
                    path = f"HF: {info['hf_repo']}"

            elif info.get("ocr_library"):
                downloaded = self._check_ocr_model_exists(
                    info["ocr_library"],
                    info.get("language"),
                )
                if downloaded:
                    path = f"OCR: {info['ocr_library'].value}"

            statuses.append(
                ModelStatus(
                    id=model_id,
                    name=info["name"],
                    description=info["description"],
                    size_mb=info["size_mb"],
                    required=info["required"],
                    downloaded=downloaded,
                    path=path,
                )
            )

        return statuses

    def get_model_table_data(self) -> list[list[str]]:
        """Get model status as table data for Gradio."""
        statuses = self.get_model_status()
        data = []

        for status in statuses:
            status_str = "Ready" if status.downloaded else "Missing"
            size_str = f"{status.size_mb}MB"
            action = "Downloaded" if status.downloaded else "Download"

            data.append([
                status.name,
                status_str,
                size_str,
                action,
            ])

        return data

    def download_hf_model(self, repo_id: str, progress_callback=None) -> bool:
        """Download a HuggingFace model to local directory.

        Note: Caller is responsible for disabling offline mode before calling this.
        """
        try:
            from huggingface_hub import snapshot_download

            if progress_callback:
                progress_callback(f"Downloading {repo_id}...")

            # Download to local huggingface directory
            cache_dir = self.huggingface_dir / "hub"
            cache_dir.mkdir(parents=True, exist_ok=True)

            snapshot_download(
                repo_id=repo_id,
                cache_dir=str(cache_dir),
            )

            if progress_callback:
                progress_callback(f"Downloaded {repo_id}")

            return True

        except Exception as e:
            if progress_callback:
                progress_callback(f"Failed to download {repo_id}: {e}")
            return False

    def download_easyocr_model(self, languages: list[str], progress_callback=None) -> bool:
        """Download EasyOCR models to local directory."""
        try:
            if progress_callback:
                progress_callback(f"Downloading EasyOCR models for {languages}...")

            # Set environment to use local directory
            os.environ["EASYOCR_MODULE_PATH"] = str(self.easyocr_dir)

            import easyocr
            # Initialize reader to trigger download
            reader = easyocr.Reader(
                languages,
                model_storage_directory=str(self.easyocr_dir),
                download_enabled=True,
                gpu=False,
                verbose=False,
            )

            if progress_callback:
                progress_callback(f"EasyOCR models downloaded for {languages}")
            return True

        except Exception as e:
            if progress_callback:
                progress_callback(f"Failed to download EasyOCR: {e}")
            return False

    def download_model(self, model_id: str, progress_callback=None) -> bool:
        """Download a specific model."""
        if model_id not in MODELS_INFO:
            return False

        info = MODELS_INFO[model_id]

        try:
            if info.get("hf_repo"):
                return self.download_hf_model(info["hf_repo"], progress_callback)

            elif info.get("ocr_library"):
                if info["ocr_library"] == OCRLibrary.EASYOCR:
                    lang = info.get("language", "en")
                    return self.download_easyocr_model([lang], progress_callback)
                elif info["ocr_library"] == OCRLibrary.RAPIDOCR:
                    if progress_callback:
                        progress_callback("RapidOCR models are bundled with the package")
                    return True
                elif info["ocr_library"] == OCRLibrary.TESSERACT:
                    if progress_callback:
                        progress_callback("Tesseract models must be installed via system package manager")
                    return False

        except Exception as e:
            if progress_callback:
                progress_callback(f"Error: {e}")
            return False

        return False

    def download_all_hf_models(self, progress_callback=None) -> dict[str, bool]:
        """Download all HuggingFace models."""
        results = {}

        for model_id, info in MODELS_INFO.items():
            if info.get("hf_repo"):
                if progress_callback:
                    progress_callback(f"Downloading {info['name']}...")
                success = self.download_hf_model(info["hf_repo"], progress_callback)
                results[model_id] = success

        return results

    def download_all_easyocr_models(self, languages: list[str] = None, progress_callback=None) -> bool:
        """Download all EasyOCR models."""
        if languages is None:
            languages = ["en", "ar"]  # Default languages

        return self.download_easyocr_model(languages, progress_callback)

    def download_all(self, include_optional: bool = False, progress_callback=None) -> dict[str, bool]:
        """Download all required (and optionally all) models."""
        results = {}

        for model_id, info in MODELS_INFO.items():
            if not include_optional and not info["required"]:
                continue

            if progress_callback:
                progress_callback(f"Checking {info['name']}...")

            success = self.download_model(model_id, progress_callback)
            results[model_id] = success

        return results

    def download_required(self, progress_callback=None) -> dict[str, bool]:
        """Download only required models."""
        return self.download_all(include_optional=False, progress_callback=progress_callback)

    def copy_from_cache(self, progress_callback=None) -> dict[str, bool]:
        """Copy models from default cache locations to local models directory."""
        results = {}

        # Copy HuggingFace models
        default_hf_cache = Path.home() / ".cache" / "huggingface" / "hub"
        if default_hf_cache.exists():
            if progress_callback:
                progress_callback("Copying HuggingFace models...")

            local_hub = self.huggingface_dir / "hub"
            local_hub.mkdir(parents=True, exist_ok=True)

            for item in default_hf_cache.iterdir():
                if item.name.startswith("models--"):
                    dest = local_hub / item.name
                    if not dest.exists():
                        if progress_callback:
                            progress_callback(f"  Copying {item.name}...")
                        try:
                            shutil.copytree(item, dest)
                            results[item.name] = True
                        except Exception as e:
                            if progress_callback:
                                progress_callback(f"  Failed: {e}")
                            results[item.name] = False

        # Copy EasyOCR models
        default_easyocr = Path.home() / ".EasyOCR" / "model"
        if default_easyocr.exists():
            if progress_callback:
                progress_callback("Copying EasyOCR models...")

            for item in default_easyocr.iterdir():
                dest = self.easyocr_dir / item.name
                if not dest.exists():
                    if progress_callback:
                        progress_callback(f"  Copying {item.name}...")
                    try:
                        shutil.copy2(item, dest)
                        results[f"easyocr_{item.name}"] = True
                    except Exception as e:
                        if progress_callback:
                            progress_callback(f"  Failed: {e}")
                        results[f"easyocr_{item.name}"] = False

        return results

    def is_offline_mode(self) -> bool:
        """Check if offline mode is enabled."""
        return is_offline_mode()

    def clear_cache(self) -> bool:
        """Clear the local models directory."""
        try:
            if self.models_dir.exists():
                shutil.rmtree(self.models_dir)
                self.models_dir.mkdir(parents=True)
                self.huggingface_dir.mkdir(parents=True)
                self.easyocr_dir.mkdir(parents=True)
            return True
        except Exception:
            return False

    def get_disk_usage(self) -> dict[str, int]:
        """Get disk usage of models directory."""
        usage = {
            "total": 0,
            "huggingface": 0,
            "easyocr": 0,
        }

        def get_size(path: Path) -> int:
            total = 0
            if path.exists():
                for item in path.rglob("*"):
                    if item.is_file():
                        total += item.stat().st_size
            return total

        usage["huggingface"] = get_size(self.huggingface_dir)
        usage["easyocr"] = get_size(self.easyocr_dir)
        usage["total"] = usage["huggingface"] + usage["easyocr"]

        return usage

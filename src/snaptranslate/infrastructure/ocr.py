from __future__ import annotations

import os
import sys
import tempfile
import warnings
from contextlib import contextmanager
from pathlib import Path
from typing import Protocol

from PIL import Image

from snaptranslate.domain.models import OcrResult


class OcrService(Protocol):
    def extract_text(self, image: Image.Image) -> OcrResult:
        ...


class PaddleOcrService:
    def __init__(self, language: str = "japan") -> None:
        self.language = language
        self._engine = None

    def _load_engine(self):
        if self._engine is not None:
            return self._engine

        os.environ.setdefault("PADDLE_PDX_DISABLE_MODEL_SOURCE_CHECK", "True")

        with _suppress_paddle_output():
            try:
                from paddleocr import PaddleOCR
            except ImportError as exc:
                raise RuntimeError(
                    "PaddleOCR is not installed. Install OCR dependencies with "
                    "`uv sync --extra ocr`. This installs both paddleocr and paddlepaddle."
                ) from exc

        # PaddleOCR v3 downloads and manages model artifacts when model dirs are omitted.
        # Passing empty custom directories makes it look for missing inference.yml files.
        with _suppress_paddle_output():
            self._engine = PaddleOCR(
                lang=self.language,
                ocr_version="PP-OCRv3",
                use_doc_orientation_classify=False,
                use_doc_unwarping=False,
                use_textline_orientation=False,
                enable_mkldnn=False,
                device="cpu",
            )
        return self._engine

    def extract_text(self, image: Image.Image) -> OcrResult:
        engine = self._load_engine()
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as temp:
            temp_path = Path(temp.name)
            image.save(temp_path)

        try:
            predict = getattr(engine, "predict", None) or engine.ocr
            with _suppress_paddle_output():
                raw = predict(str(temp_path))
        finally:
            temp_path.unlink(missing_ok=True)

        lines: list[str] = []
        for page in raw or []:
            lines.extend(_extract_page_text(page))
        return OcrResult("\n".join(line.strip() for line in lines if line.strip()))


def _extract_page_text(page) -> list[str]:
    if isinstance(page, dict):
        rec_texts = page.get("rec_texts")
        if isinstance(rec_texts, list):
            return [str(text) for text in rec_texts]

    if hasattr(page, "json"):
        try:
            data = page.json
            if isinstance(data, dict):
                return _extract_page_text(data)
        except Exception:
            pass

    lines: list[str] = []
    for item in page or []:
        if len(item) >= 2 and item[1]:
            lines.append(str(item[1][0]))
    return lines


@contextmanager
def _suppress_paddle_output():
    if os.environ.get("SNAPTRANSLATE_PADDLE_VERBOSE") == "1":
        yield
        return

    stdout_fd = sys.stdout.fileno()
    stderr_fd = sys.stderr.fileno()
    saved_stdout_fd = os.dup(stdout_fd)
    saved_stderr_fd = os.dup(stderr_fd)
    try:
        sys.stdout.flush()
        sys.stderr.flush()
        with open(os.devnull, "w", encoding="utf-8") as devnull, warnings.catch_warnings():
            os.dup2(devnull.fileno(), stdout_fd)
            os.dup2(devnull.fileno(), stderr_fd)
            warnings.filterwarnings("ignore", message="No ccache found.*")
            warnings.filterwarnings("ignore", category=DeprecationWarning)
            yield
    finally:
        sys.stdout.flush()
        sys.stderr.flush()
        os.dup2(saved_stdout_fd, stdout_fd)
        os.dup2(saved_stderr_fd, stderr_fd)
        os.close(saved_stdout_fd)
        os.close(saved_stderr_fd)

from __future__ import annotations

import tempfile
from pathlib import Path
from typing import Protocol

from PIL import Image

from snaptranslate.domain.models import OcrResult
from snaptranslate.infrastructure.paths import local_data_dir


class OcrService(Protocol):
    def extract_text(self, image: Image.Image) -> OcrResult:
        ...


class PaddleOcrService:
    def __init__(self, language: str = "japan") -> None:
        self.language = language
        self.model_dir = local_data_dir() / "paddleocr"
        self.model_dir.mkdir(parents=True, exist_ok=True)
        self._engine = None

    def _load_engine(self):
        if self._engine is not None:
            return self._engine

        try:
            from paddleocr import PaddleOCR
        except ImportError as exc:
            raise RuntimeError(
                "PaddleOCR is not installed. Install OCR dependencies with "
                "`uv sync --extra ocr`. This installs both paddleocr and paddlepaddle."
            ) from exc

        self._engine = PaddleOCR(
            use_angle_cls=True,
            lang=self.language,
            det_model_dir=str(self.model_dir / "det"),
            rec_model_dir=str(self.model_dir / "rec"),
            cls_model_dir=str(self.model_dir / "cls"),
        )
        return self._engine

    def extract_text(self, image: Image.Image) -> OcrResult:
        engine = self._load_engine()
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as temp:
            temp_path = Path(temp.name)
            image.save(temp_path)

        try:
            raw = engine.ocr(str(temp_path), cls=True)
        finally:
            temp_path.unlink(missing_ok=True)

        lines: list[str] = []
        for page in raw or []:
            for item in page or []:
                if len(item) >= 2 and item[1]:
                    lines.append(str(item[1][0]))
        return OcrResult("\n".join(line.strip() for line in lines if line.strip()))

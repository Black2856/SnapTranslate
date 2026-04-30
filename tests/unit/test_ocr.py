from __future__ import annotations

import sys
from pathlib import Path
from types import ModuleType

from snaptranslate.infrastructure.ocr import PaddleOcrService


def test_paddle_ocr_disables_mkldnn(monkeypatch) -> None:
    captured: dict[str, object] = {}

    class FakePaddleOCR:
        def __init__(self, **kwargs) -> None:
            captured.update(kwargs)

    fake_module = ModuleType("paddleocr")
    fake_module.PaddleOCR = FakePaddleOCR
    monkeypatch.setitem(sys.modules, "paddleocr", fake_module)

    PaddleOcrService("en")._load_engine()

    assert captured["lang"] == "en"
    assert captured["ocr_version"] == "PP-OCRv3"
    assert captured["use_textline_orientation"] is False
    assert captured["enable_mkldnn"] is False
    assert captured["device"] == "cpu"


def test_extract_text_uses_predict(monkeypatch) -> None:
    captured_path: dict[str, str] = {}

    class FakeEngine:
        def predict(self, image_path: str):
            captured_path["value"] = image_path
            return [{"rec_texts": ["hello", "world"]}]

    service = PaddleOcrService("en")
    service._engine = FakeEngine()

    from PIL import Image

    image = Image.new("RGB", (10, 10), "white")

    result = service.extract_text(image)

    assert result.text == "hello\nworld"
    assert not Path(captured_path["value"]).exists()


def test_suppress_paddle_output_falls_back_when_stream_has_no_fd(monkeypatch) -> None:
    from snaptranslate.infrastructure import ocr

    with ocr._suppress_paddle_output():
        reached = True

    assert reached is True

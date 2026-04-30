from __future__ import annotations

import sys
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
    assert captured["enable_mkldnn"] is False
    assert captured["device"] == "cpu"

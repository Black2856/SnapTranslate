from __future__ import annotations

import sys
from types import ModuleType

from PIL import Image

from snaptranslate.domain.models import AppSettings
from snaptranslate.infrastructure.translator import ChatGptTranslator


class FakeResponse:
    output_text = "translated"


def test_chatgpt_translator_sends_image_input(monkeypatch) -> None:
    captured: dict[str, object] = {}

    class FakeResponses:
        def create(self, **kwargs):
            captured.update(kwargs)
            return FakeResponse()

    class FakeOpenAI:
        def __init__(self, **kwargs) -> None:
            self.responses = FakeResponses()

    fake_module = ModuleType("openai")
    fake_module.OpenAI = FakeOpenAI
    monkeypatch.setitem(sys.modules, "openai", fake_module)
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")

    image = Image.new("RGB", (1, 1), "white")
    result = ChatGptTranslator(AppSettings()).translate_image(image, "translate this")

    content = captured["input"][0]["content"]
    assert result.text == "translated"
    assert content[0] == {"type": "input_text", "text": "translate this"}
    assert content[1]["type"] == "input_image"
    assert content[1]["image_url"].startswith("data:image/png;base64,")

from __future__ import annotations

import os
from typing import Protocol

from snaptranslate.domain.models import AppSettings, TranslationResult
from snaptranslate.infrastructure.image_encoder import ImageEncoder, PngDataUrlEncoder


class TextTranslator(Protocol):
    def translate_text(self, text: str, prompt: str) -> TranslationResult:
        ...


class ImageTranslator(Protocol):
    def translate_image(self, image, prompt: str) -> TranslationResult:
        ...


class ChatGptTranslator:
    def __init__(self, settings: AppSettings, image_encoder: ImageEncoder | None = None) -> None:
        self.settings = settings
        self.image_encoder = image_encoder or PngDataUrlEncoder()

    def translate(self, text: str, prompt: str) -> TranslationResult:
        return self.translate_text(text, prompt)

    def translate_text(self, text: str, prompt: str) -> TranslationResult:
        if not text.strip():
            raise ValueError("Translation text is empty.")

        rendered_prompt = prompt.replace("{text}", text)
        client = self._client()
        response = client.responses.create(
            model=self.settings.chatgpt_model,
            input=rendered_prompt,
        )
        return self._result_from_response(response)

    def translate_image(self, image, prompt: str) -> TranslationResult:
        data_url = self.image_encoder.to_data_url(image)
        client = self._client()
        response = client.responses.create(
            model=self.settings.chatgpt_model,
            input=[
                {
                    "role": "user",
                    "content": [
                        {"type": "input_text", "text": prompt},
                        {"type": "input_image", "image_url": data_url},
                    ],
                }
            ],
        )
        return self._result_from_response(response)

    def _client(self):
        api_key = self._api_key()
        if not api_key:
            raise RuntimeError("OPENAI_API_KEY is not set.")

        try:
            from openai import OpenAI
        except ImportError as exc:
            raise RuntimeError("openai package is not installed.") from exc

        return OpenAI(api_key=api_key, timeout=self.settings.request_timeout_seconds)

    def _result_from_response(self, response) -> TranslationResult:
        translated = getattr(response, "output_text", "").strip()
        if not translated:
            raise RuntimeError("Translation response was empty.")
        return TranslationResult(text=translated, model=self.settings.chatgpt_model)

    def _api_key(self) -> str:
        if self.settings.api_key_source.value == "config" and self.settings.api_key:
            return self.settings.api_key
        return os.getenv("OPENAI_API_KEY", "")


class EchoTranslator:
    """Test translator used when API calls are not desired."""

    def __init__(self, model: str = "echo") -> None:
        self.model = model

    def translate(self, text: str, prompt: str) -> TranslationResult:
        return self.translate_text(text, prompt)

    def translate_text(self, text: str, prompt: str) -> TranslationResult:
        return TranslationResult(text=text, model=self.model)

    def translate_image(self, image, prompt: str) -> TranslationResult:
        return TranslationResult(text=prompt, model=self.model)

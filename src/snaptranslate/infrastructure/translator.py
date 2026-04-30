from __future__ import annotations

import os
from typing import Protocol

from snaptranslate.domain.models import AppSettings, TranslationResult


class Translator(Protocol):
    def translate(self, text: str, prompt: str) -> TranslationResult:
        ...


class ChatGptTranslator:
    def __init__(self, settings: AppSettings) -> None:
        self.settings = settings

    def translate(self, text: str, prompt: str) -> TranslationResult:
        if not text.strip():
            raise ValueError("Translation text is empty.")

        api_key = self._api_key()
        if not api_key:
            raise RuntimeError("OPENAI_API_KEY is not set.")

        try:
            from openai import OpenAI
        except ImportError as exc:
            raise RuntimeError("openai package is not installed.") from exc

        rendered_prompt = prompt.replace("{text}", text)
        client = OpenAI(api_key=api_key, timeout=self.settings.request_timeout_seconds)
        response = client.responses.create(
            model=self.settings.chatgpt_model,
            input=rendered_prompt,
        )
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
        return TranslationResult(text=text, model=self.model)


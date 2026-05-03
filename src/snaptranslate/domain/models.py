from __future__ import annotations

from dataclasses import asdict, dataclass, field, fields
from enum import Enum
from typing import Any


class RegionMode(str, Enum):
    SAVED = "saved"
    INTERACTIVE = "interactive"


class ApiKeySource(str, Enum):
    ENV = "env"
    CONFIG = "config"


class ReadResultDisplayMode(str, Enum):
    OVERLAY = "overlay"
    WINDOW = "window"


class UiLanguage(str, Enum):
    EN = "en"
    JA = "ja"


@dataclass(frozen=True)
class ScreenRegion:
    left: int
    top: int
    width: int
    height: int

    def validate(self) -> None:
        if self.width <= 0 or self.height <= 0:
            raise ValueError("Screen region width and height must be positive.")

    @property
    def box(self) -> tuple[int, int, int, int]:
        return (self.left, self.top, self.left + self.width, self.top + self.height)

    @classmethod
    def from_dict(cls, data: dict[str, Any] | None) -> ScreenRegion | None:
        if not data:
            return None
        region = cls(
            left=int(data["left"]),
            top=int(data["top"]),
            width=int(data["width"]),
            height=int(data["height"]),
        )
        region.validate()
        return region


@dataclass(frozen=True)
class Hotkey:
    value: str

    def normalized(self) -> str:
        return "+".join(part.strip().title() for part in self.value.split("+") if part.strip())

    def parts(self) -> list[str]:
        return [part.strip().lower() for part in self.value.split("+") if part.strip()]

    def validate(self) -> None:
        parts = self.parts()
        if not parts:
            raise ValueError("Hotkey is empty.")
        key_parts = [part for part in parts if part not in {"ctrl", "control", "shift", "alt", "win"}]
        if len(key_parts) != 1:
            raise ValueError(f"Hotkey must contain exactly one non-modifier key: {self.value}")


@dataclass
class AppSettings:
    ui_language: UiLanguage = UiLanguage.EN
    read_hotkey: str = "Ctrl+Shift+F8"
    input_hotkey: str = "Ctrl+Shift+F9"
    region_mode: RegionMode = RegionMode.SAVED
    saved_region: ScreenRegion | None = None
    show_status: bool = True
    read_image_prompt: str = (
        "Read the text in the image and translate it naturally. Return only the translation."
    )
    input_translation_prompt: str = (
        "Translate the input text naturally. Return only the translation.\n\n{text}"
    )
    chatgpt_model: str = "gpt-5.4-mini"
    read_result_display_mode: ReadResultDisplayMode = ReadResultDisplayMode.OVERLAY
    overlay_text_color: str = "#FFFFFF"
    overlay_font_family: str = "Yu Gothic UI"
    overlay_font_size: int = 18
    api_key_source: ApiKeySource = ApiKeySource.ENV
    api_key: str = ""
    keep_draft_on_hide: bool = True
    enable_history: bool = False
    history_path: str = "%APPDATA%/SnapTranslate/history.jsonl"
    request_timeout_seconds: float = 30

    def validate(self) -> None:
        Hotkey(self.read_hotkey).validate()
        Hotkey(self.input_hotkey).validate()
        if Hotkey(self.read_hotkey).normalized() == Hotkey(self.input_hotkey).normalized():
            raise ValueError("Read and input hotkeys must be different.")
        if self.saved_region:
            self.saved_region.validate()
        if self.overlay_font_size <= 0:
            raise ValueError("Overlay font size must be positive.")
        if self.request_timeout_seconds <= 0:
            raise ValueError("Request timeout must be positive.")

    def to_json_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["ui_language"] = self.ui_language.value
        data["region_mode"] = self.region_mode.value
        data["api_key_source"] = self.api_key_source.value
        data["read_result_display_mode"] = self.read_result_display_mode.value
        return data

    @classmethod
    def from_json_dict(cls, data: dict[str, Any]) -> AppSettings:
        defaults = cls()
        migrated = dict(data)
        if "read_image_prompt" not in migrated and "read_translation_prompt" in migrated:
            migrated["read_image_prompt"] = migrated["read_translation_prompt"]
        migrated.pop("read_translation_prompt", None)
        migrated.pop("ocr_language", None)

        valid_fields = {field.name for field in fields(cls)}
        filtered = {key: value for key, value in migrated.items() if key in valid_fields}
        merged = {**defaults.to_json_dict(), **filtered}
        merged["ui_language"] = UiLanguage(merged["ui_language"])
        merged["region_mode"] = RegionMode(merged["region_mode"])
        merged["api_key_source"] = ApiKeySource(merged["api_key_source"])
        merged["read_result_display_mode"] = ReadResultDisplayMode(
            merged["read_result_display_mode"]
        )
        merged["saved_region"] = ScreenRegion.from_dict(merged.get("saved_region"))
        settings = cls(**merged)
        settings.validate()
        return settings


@dataclass(frozen=True)
class OcrResult:
    text: str


@dataclass(frozen=True)
class TranslationResult:
    text: str
    model: str


@dataclass(frozen=True)
class HistoryEntry:
    timestamp: str
    mode: str
    source_text: str
    translated_text: str
    model: str
    metadata: dict[str, Any] = field(default_factory=dict)

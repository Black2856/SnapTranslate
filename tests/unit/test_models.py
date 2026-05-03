from __future__ import annotations

import pytest

from snaptranslate.domain.models import AppSettings, Hotkey, ScreenRegion, UiLanguage


def test_hotkey_requires_one_key() -> None:
    Hotkey("Ctrl+Enter").validate()

    with pytest.raises(ValueError):
        Hotkey("Ctrl+Shift").validate()


def test_settings_reject_duplicate_hotkeys() -> None:
    settings = AppSettings(read_hotkey="Ctrl+F8", input_hotkey="Ctrl+F8")

    with pytest.raises(ValueError):
        settings.validate()


def test_screen_region_box() -> None:
    region = ScreenRegion(left=10, top=20, width=30, height=40)

    assert region.box == (10, 20, 40, 60)


def test_settings_serializes_ui_language() -> None:
    settings = AppSettings(ui_language=UiLanguage.JA)

    loaded = AppSettings.from_json_dict(settings.to_json_dict())

    assert loaded.ui_language == UiLanguage.JA


def test_default_settings_match_distribution_defaults() -> None:
    settings = AppSettings()

    assert settings.ui_language == UiLanguage.JA
    assert settings.read_hotkey == "Ctrl+Enter"
    assert settings.input_hotkey == "Shift+Enter"
    assert settings.read_image_prompt == (
        "Read the text in the image and translate it naturally. Return only the translation."
    )
    assert settings.overlay_font_size == 12
    assert settings.read_box_color == "#000000"
    assert settings.request_timeout_seconds == 10.0


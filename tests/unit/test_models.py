from __future__ import annotations

import pytest

from snaptranslate.domain.models import AppSettings, Hotkey, ScreenRegion, UiLanguage


def test_hotkey_requires_one_key() -> None:
    Hotkey("Ctrl+Shift+F8").validate()

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


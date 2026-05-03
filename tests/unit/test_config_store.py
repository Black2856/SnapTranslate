from __future__ import annotations

from pathlib import Path

from snaptranslate.domain.models import (
    ApiKeySource,
    AppSettings,
    ReadResultDisplayMode,
    RegionMode,
    ScreenRegion,
    UiLanguage,
)
from snaptranslate.infrastructure.config_store import ConfigStore


def test_config_round_trip() -> None:
    path = Path("tests/.tmp_config.json")
    path.unlink(missing_ok=True)
    store = ConfigStore(path)
    settings = AppSettings(
        region_mode=RegionMode.SAVED,
        saved_region=ScreenRegion(1, 2, 3, 4),
        api_key_source=ApiKeySource.CONFIG,
        api_key="sk-test",
        read_result_display_mode=ReadResultDisplayMode.WINDOW,
        ui_language=UiLanguage.JA,
        read_box_color="#202020",
        request_timeout_seconds=45,
        enable_history=True,
    )

    store.save(settings)
    loaded = store.load()

    assert loaded.saved_region == ScreenRegion(1, 2, 3, 4)
    assert loaded.api_key_source == ApiKeySource.CONFIG
    assert loaded.api_key == "sk-test"
    assert loaded.read_result_display_mode == ReadResultDisplayMode.WINDOW
    assert loaded.ui_language == UiLanguage.JA
    assert loaded.read_box_color == "#202020"
    assert loaded.request_timeout_seconds == 45
    assert loaded.enable_history is True
    path.unlink(missing_ok=True)

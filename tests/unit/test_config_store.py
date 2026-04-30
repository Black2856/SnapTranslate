from __future__ import annotations

from pathlib import Path

from snaptranslate.domain.models import AppSettings, RegionMode, ScreenRegion
from snaptranslate.infrastructure.config_store import ConfigStore


def test_config_round_trip() -> None:
    path = Path("tests/.tmp_config.json")
    path.unlink(missing_ok=True)
    store = ConfigStore(path)
    settings = AppSettings(
        region_mode=RegionMode.SAVED,
        saved_region=ScreenRegion(1, 2, 3, 4),
        enable_history=True,
    )

    store.save(settings)
    loaded = store.load()

    assert loaded.saved_region == ScreenRegion(1, 2, 3, 4)
    assert loaded.enable_history is True
    path.unlink(missing_ok=True)

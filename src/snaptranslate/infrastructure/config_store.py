from __future__ import annotations

import json
from pathlib import Path

from snaptranslate.domain.models import AppSettings
from snaptranslate.infrastructure.paths import app_data_dir


class ConfigStore:
    def __init__(self, path: Path | None = None) -> None:
        self.path = path or app_data_dir() / "config.json"

    def load(self) -> AppSettings:
        if not self.path.exists():
            settings = AppSettings()
            self.save(settings)
            return settings

        with self.path.open("r", encoding="utf-8") as file:
            data = json.load(file)
        return AppSettings.from_json_dict(data)

    def save(self, settings: AppSettings) -> None:
        settings.validate()
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("w", encoding="utf-8") as file:
            json.dump(settings.to_json_dict(), file, ensure_ascii=False, indent=2)
            file.write("\n")


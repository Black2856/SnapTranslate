from __future__ import annotations

import json
from dataclasses import asdict

from snaptranslate.domain.models import HistoryEntry
from snaptranslate.infrastructure.paths import expand_path


class HistoryStore:
    def __init__(self, path: str) -> None:
        self.path = expand_path(path)

    def append(self, entry: HistoryEntry) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("a", encoding="utf-8") as file:
            json.dump(asdict(entry), file, ensure_ascii=False)
            file.write("\n")

from __future__ import annotations

import json
from pathlib import Path

from snaptranslate.domain.models import HistoryEntry
from snaptranslate.infrastructure.history_store import HistoryStore


def test_history_store_appends_jsonl() -> None:
    path = Path("tests/.tmp_history.jsonl")
    path.unlink(missing_ok=True)
    store = HistoryStore(str(path))

    store.append(
        HistoryEntry(
            timestamp="2026-04-30T00:00:00+00:00",
            mode="input",
            source_text="hello",
            translated_text="こんにちは",
            model="test",
        )
    )

    data = json.loads(path.read_text(encoding="utf-8"))
    assert data["source_text"] == "hello"
    assert data["translated_text"] == "こんにちは"
    path.unlink(missing_ok=True)

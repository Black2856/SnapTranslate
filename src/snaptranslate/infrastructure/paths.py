from __future__ import annotations

import os
from pathlib import Path


APP_NAME = "SnapTranslate"


def app_data_dir() -> Path:
    base = os.getenv("APPDATA") or str(Path.home() / "AppData" / "Roaming")
    path = Path(base) / APP_NAME
    path.mkdir(parents=True, exist_ok=True)
    return path


def local_data_dir() -> Path:
    base = os.getenv("LOCALAPPDATA") or str(Path.home() / "AppData" / "Local")
    path = Path(base) / APP_NAME
    path.mkdir(parents=True, exist_ok=True)
    return path


def expand_path(value: str) -> Path:
    expanded = os.path.expandvars(value)
    return Path(expanded).expanduser()


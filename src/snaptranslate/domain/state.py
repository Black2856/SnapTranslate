from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from threading import Lock


class ReadState(str, Enum):
    IDLE = "idle"
    REGION_SELECTING = "region_selecting"
    OCR_RUNNING = "ocr_running"
    TRANSLATING = "translating"
    OVERLAY_VISIBLE = "overlay_visible"
    ERROR = "error"


class InputState(str, Enum):
    HIDDEN = "hidden"
    VISIBLE = "visible"
    TRANSLATING = "translating"
    COPIED = "copied"
    ERROR = "error"


@dataclass
class StateSnapshot:
    read: ReadState
    input: InputState
    message: str = ""


class AppState:
    def __init__(self) -> None:
        self._read = ReadState.IDLE
        self._input = InputState.HIDDEN
        self._message = ""
        self._lock = Lock()

    def snapshot(self) -> StateSnapshot:
        with self._lock:
            return StateSnapshot(self._read, self._input, self._message)

    def set_read(self, state: ReadState, message: str = "") -> None:
        with self._lock:
            self._read = state
            self._message = message

    def set_input(self, state: InputState, message: str = "") -> None:
        with self._lock:
            self._input = state
            self._message = message

    def is_read_busy(self) -> bool:
        with self._lock:
            return self._read in {
                ReadState.REGION_SELECTING,
                ReadState.OCR_RUNNING,
                ReadState.TRANSLATING,
            }

    def is_input_busy(self) -> bool:
        with self._lock:
            return self._input == InputState.TRANSLATING


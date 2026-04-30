from __future__ import annotations

import logging
import threading
from collections.abc import Callable

from snaptranslate.domain.models import Hotkey

logger = logging.getLogger(__name__)


class HotkeyController:
    READ_ID = 1
    INPUT_ID = 2

    def __init__(self, read_hotkey: str, input_hotkey: str, on_read: Callable[[], None], on_input: Callable[[], None]) -> None:
        self.read_hotkey = read_hotkey
        self.input_hotkey = input_hotkey
        self.on_read = on_read
        self.on_input = on_input
        self._thread: threading.Thread | None = None
        self._stop_event = threading.Event()
        self._thread_id: int | None = None

    def start(self) -> None:
        if self._thread and self._thread.is_alive():
            return
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._run, name="hotkey-listener", daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self._stop_event.set()
        if self._thread_id:
            try:
                import win32api
                import win32con

                win32api.PostThreadMessage(self._thread_id, win32con.WM_QUIT, 0, 0)
            except Exception:
                logger.debug("Failed to post hotkey quit message", exc_info=True)

    def _run(self) -> None:
        import win32api
        import win32con
        import win32gui

        self._thread_id = win32api.GetCurrentThreadId()
        read_mod, read_vk = hotkey_to_win32(Hotkey(self.read_hotkey))
        input_mod, input_vk = hotkey_to_win32(Hotkey(self.input_hotkey))

        try:
            win32gui.RegisterHotKey(None, self.READ_ID, read_mod, read_vk)
            win32gui.RegisterHotKey(None, self.INPUT_ID, input_mod, input_vk)
            while not self._stop_event.is_set():
                msg = win32gui.GetMessage(None, 0, 0)
                if not msg or msg[1][1] == win32con.WM_QUIT:
                    break
                message = msg[1]
                if message[1] == win32con.WM_HOTKEY:
                    if message[2] == self.READ_ID:
                        self.on_read()
                    elif message[2] == self.INPUT_ID:
                        self.on_input()
        finally:
            try:
                win32gui.UnregisterHotKey(None, self.READ_ID)
                win32gui.UnregisterHotKey(None, self.INPUT_ID)
            except Exception:
                logger.debug("Failed to unregister hotkeys", exc_info=True)


def hotkey_to_win32(hotkey: Hotkey) -> tuple[int, int]:
    import win32con

    hotkey.validate()
    modifiers = 0
    key = ""
    for part in hotkey.parts():
        if part in {"ctrl", "control"}:
            modifiers |= win32con.MOD_CONTROL
        elif part == "shift":
            modifiers |= win32con.MOD_SHIFT
        elif part == "alt":
            modifiers |= win32con.MOD_ALT
        elif part == "win":
            modifiers |= win32con.MOD_WIN
        else:
            key = part

    vk = _key_to_vk(key)
    return modifiers, vk


def _key_to_vk(key: str) -> int:
    import win32con

    upper = key.upper()
    if len(upper) == 1 and upper.isalnum():
        return ord(upper)
    if upper.startswith("F") and upper[1:].isdigit():
        number = int(upper[1:])
        if 1 <= number <= 24:
            return win32con.VK_F1 + number - 1
    special = {
        "ESC": win32con.VK_ESCAPE,
        "ESCAPE": win32con.VK_ESCAPE,
        "SPACE": win32con.VK_SPACE,
        "TAB": win32con.VK_TAB,
        "ENTER": win32con.VK_RETURN,
    }
    if upper in special:
        return special[upper]
    raise ValueError(f"Unsupported hotkey key: {key}")


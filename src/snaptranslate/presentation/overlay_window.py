from __future__ import annotations

import queue
import tkinter as tk
from collections.abc import Callable

from snaptranslate.domain.models import AppSettings, ReadResultDisplayMode, ScreenRegion


class OverlayWindow:
    def __init__(self, root: tk.Tk, on_close: Callable[[], None] | None = None) -> None:
        self.root = root
        self.on_close = on_close
        self.background_color = "#000000"
        self.window: tk.Toplevel
        self.label: tk.Label
        self._show_requests: queue.Queue[tuple[str, ScreenRegion, AppSettings]] = queue.Queue()
        self._create_window()
        self.root.after(50, self._drain_show_requests)

    def _create_window(self) -> None:
        self.window = tk.Toplevel(self.root)
        self.window.title("SnapTranslate Overlay")
        self.window.overrideredirect(True)
        self.window.attributes("-topmost", True)
        self.window.attributes("-alpha", 1.0)
        self.window.configure(bg=self.background_color)
        self.window.protocol("WM_DELETE_WINDOW", self._handle_close)
        self.label = tk.Label(
            self.window,
            text="",
            bg=self.background_color,
            justify="left",
            wraplength=400,
            padx=4,
            pady=2,
        )
        self.label.pack(fill="both", expand=True)
        self.window.withdraw()
        self._configure_as_overlay()

    def show_text(self, text: str, region: ScreenRegion, settings: AppSettings) -> None:
        self._show_requests.put((text, region, settings))

    def _drain_show_requests(self) -> None:
        request = None
        while True:
            try:
                request = self._show_requests.get_nowait()
            except queue.Empty:
                break
        if request is not None:
            text, region, settings = request
            self._show_text(text, region, settings)
        self.root.after(50, self._drain_show_requests)

    def _show_text(self, text: str, region: ScreenRegion, settings: AppSettings) -> None:
        if not self.window.winfo_exists() or not self.label.winfo_exists():
            self._create_window()
        self.label.configure(
            text=text,
            fg=settings.overlay_text_color,
            bg=self.background_color,
            font=(settings.overlay_font_family, settings.overlay_font_size),
            wraplength=max(20, region.width),
        )
        if settings.read_result_display_mode == ReadResultDisplayMode.WINDOW:
            self._configure_as_window()
        else:
            self._configure_as_overlay()
        self.window.geometry(f"{region.width}x{region.height}+{region.left}+{region.top}")
        self.window.deiconify()
        self._bring_to_front(region)

    def hide(self) -> None:
        self.root.after(0, self.window.withdraw)

    def _handle_close(self) -> None:
        self.window.withdraw()
        if self.on_close:
            self.on_close()

    def _configure_as_overlay(self) -> None:
        self.window.title("SnapTranslate Overlay")
        self.window.overrideredirect(True)
        self._set_click_through(True)

    def _configure_as_window(self) -> None:
        self.window.title("SnapTranslate Read Result")
        self.window.overrideredirect(False)
        self._set_click_through(False)

    def _set_click_through(self, enabled: bool) -> None:
        try:
            import win32con
            import win32gui

            hwnd = self.window.winfo_id()
            style = win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)
            style &= ~win32con.WS_EX_LAYERED
            if enabled:
                style |= win32con.WS_EX_TRANSPARENT
            else:
                style &= ~win32con.WS_EX_TRANSPARENT
            style |= win32con.WS_EX_TOPMOST
            win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE, style)
        except Exception:
            pass

    def _bring_to_front(self, region: ScreenRegion) -> None:
        self.window.attributes("-topmost", True)
        self.window.lift()
        try:
            import win32con
            import win32gui

            hwnd = self.window.winfo_id()
            win32gui.SetWindowPos(
                hwnd,
                win32con.HWND_TOPMOST,
                region.left,
                region.top,
                region.width,
                region.height,
                win32con.SWP_NOACTIVATE | win32con.SWP_SHOWWINDOW,
            )
        except Exception:
            pass

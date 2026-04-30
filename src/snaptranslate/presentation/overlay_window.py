from __future__ import annotations

import tkinter as tk

from snaptranslate.domain.models import AppSettings, ScreenRegion


class OverlayWindow:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.window = tk.Toplevel(root)
        self.window.title("SnapTranslate Overlay")
        self.window.overrideredirect(True)
        self.window.attributes("-topmost", True)
        self.window.attributes("-alpha", 1.0)
        self.background_color = "#000000"
        self.window.configure(bg=self.background_color)
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
        self._make_click_through()

    def show_text(self, text: str, region: ScreenRegion, settings: AppSettings) -> None:
        self.root.after(0, self._show_text, text, region, settings)

    def _show_text(self, text: str, region: ScreenRegion, settings: AppSettings) -> None:
        self.label.configure(
            text=text,
            fg=settings.overlay_text_color,
            bg=self.background_color,
            font=(settings.overlay_font_family, settings.overlay_font_size),
            wraplength=max(20, region.width),
        )
        self.window.geometry(f"{region.width}x{region.height}+{region.left}+{region.top}")
        self.window.deiconify()
        self.window.lift()
        self._make_click_through()

    def hide(self) -> None:
        self.root.after(0, self.window.withdraw)

    def _make_click_through(self) -> None:
        try:
            import win32con
            import win32gui

            hwnd = self.window.winfo_id()
            style = win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)
            style &= ~win32con.WS_EX_LAYERED
            style |= win32con.WS_EX_TRANSPARENT | win32con.WS_EX_TOPMOST
            win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE, style)
        except Exception:
            pass

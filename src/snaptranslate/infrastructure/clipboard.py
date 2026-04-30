from __future__ import annotations


class ClipboardService:
    def copy_text(self, text: str) -> None:
        try:
            import win32clipboard
            import win32con
        except ImportError:
            self._copy_with_tk(text)
            return

        win32clipboard.OpenClipboard()
        try:
            win32clipboard.EmptyClipboard()
            win32clipboard.SetClipboardData(win32con.CF_UNICODETEXT, text)
        finally:
            win32clipboard.CloseClipboard()

    def _copy_with_tk(self, text: str) -> None:
        import tkinter as tk

        root = tk.Tk()
        root.withdraw()
        root.clipboard_clear()
        root.clipboard_append(text)
        root.update()
        root.destroy()


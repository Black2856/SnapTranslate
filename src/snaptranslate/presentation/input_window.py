from __future__ import annotations

import tkinter as tk
from collections.abc import Callable


class InputWindow:
    def __init__(self, root: tk.Tk, on_submit: Callable[[str], None]) -> None:
        self.root = root
        self.on_submit = on_submit
        self.window = tk.Toplevel(root)
        self.window.title("SnapTranslate Input")
        self.window.attributes("-topmost", True)
        self.window.geometry("560x96+120+120")
        self.window.minsize(360, 88)
        self.window.withdraw()
        self.window.protocol("WM_DELETE_WINDOW", lambda: self.hide(keep_draft=True))

        self.text = tk.Text(self.window, height=3, wrap="word", font=("Yu Gothic UI", 11))
        self.text.pack(fill="both", expand=True, padx=8, pady=(8, 4))
        self.message = tk.Label(self.window, text="Enter: translate, Shift+Enter: newline", anchor="w")
        self.message.pack(fill="x", padx=8, pady=(0, 8))

        self.text.bind("<Return>", self._on_enter)
        self.text.bind("<Shift-Return>", self._on_shift_enter)

    def show(self) -> None:
        self.window.deiconify()
        self.window.lift()
        self.text.focus_set()

    def hide(self, keep_draft: bool) -> None:
        if not keep_draft:
            self.text.delete("1.0", "end")
        self.window.withdraw()

    def is_visible(self) -> bool:
        return bool(self.window.winfo_viewable())

    def get_text(self) -> str:
        return self.text.get("1.0", "end").strip()

    def mark_copied(self) -> None:
        self.message.configure(text="Copied translation to clipboard.")

    def mark_canceled(self) -> None:
        self.message.configure(text="Canceled translation.")

    def mark_error(self, message: str) -> None:
        self.message.configure(text=f"Error: {message}")

    def _on_enter(self, event) -> str:
        self.on_submit(self.get_text())
        self.hide(keep_draft=False)
        return "break"

    def _on_shift_enter(self, event) -> None:
        self.text.insert("insert", "\n")
        return "break"

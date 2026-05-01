from __future__ import annotations

import queue
import tkinter as tk


class StatusWindow:
    def __init__(self, root: tk.Tk, visible: bool = True) -> None:
        self.root = root
        self.window = tk.Toplevel(root)
        self.window.title("SnapTranslate Status")
        self.window.overrideredirect(True)
        self.window.attributes("-topmost", True)
        self.window.configure(bg="#202020")
        self.label = tk.Label(
            self.window,
            text="[idle]",
            fg="#FFFFFF",
            bg="#202020",
            font=("Yu Gothic UI", 9),
            padx=8,
            pady=4,
        )
        self.label.pack()
        self._visible = visible
        self._messages: queue.Queue[str] = queue.Queue()
        self._position()
        if visible:
            self.window.deiconify()
        else:
            self.window.withdraw()
        self.root.after(50, self._drain_messages)

    def _position(self) -> None:
        self.window.update_idletasks()
        width = self.window.winfo_reqwidth()
        screen_width = self.window.winfo_screenwidth()
        self.window.geometry(f"+{screen_width - width - 16}+16")

    def set_message(self, message: str) -> None:
        self._messages.put(message)

    def _drain_messages(self) -> None:
        message = None
        while True:
            try:
                message = self._messages.get_nowait()
            except queue.Empty:
                break
        if message is not None:
            self._set_message(message)
        self.root.after(50, self._drain_messages)

    def _set_message(self, message: str) -> None:
        self.label.configure(text=message)
        self._position()
        if self._visible:
            self.window.deiconify()

    def set_visible(self, visible: bool) -> None:
        self._visible = visible
        if visible:
            self.window.deiconify()
            self._position()
        else:
            self.window.withdraw()


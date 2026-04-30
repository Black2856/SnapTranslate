from __future__ import annotations

import tkinter as tk

from snaptranslate.domain.models import ScreenRegion


class RegionSelector:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root

    def select_region(self) -> ScreenRegion | None:
        selector = _RegionSelectorDialog(self.root)
        self.root.wait_window(selector.window)
        return selector.region


class _RegionSelectorDialog:
    def __init__(self, root: tk.Tk) -> None:
        self.region: ScreenRegion | None = None
        self.start_x = 0
        self.start_y = 0

        self.window = tk.Toplevel(root)
        self.window.attributes("-fullscreen", True)
        self.window.attributes("-topmost", True)
        self.window.attributes("-alpha", 0.25)
        self.window.configure(bg="black")
        self.canvas = tk.Canvas(self.window, cursor="cross", bg="black", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        self.rect_id = None
        self.canvas.bind("<ButtonPress-1>", self._start)
        self.canvas.bind("<B1-Motion>", self._drag)
        self.canvas.bind("<ButtonRelease-1>", self._end)
        self.window.bind("<Escape>", self._cancel)

    def _start(self, event) -> None:
        self.start_x = event.x_root
        self.start_y = event.y_root
        self.rect_id = self.canvas.create_rectangle(event.x, event.y, event.x, event.y, outline="white", width=2)

    def _drag(self, event) -> None:
        if self.rect_id is not None:
            self.canvas.coords(
                self.rect_id,
                self.start_x,
                self.start_y,
                event.x_root,
                event.y_root,
            )

    def _end(self, event) -> None:
        left = min(self.start_x, event.x_root)
        top = min(self.start_y, event.y_root)
        width = abs(event.x_root - self.start_x)
        height = abs(event.y_root - self.start_y)
        if width > 5 and height > 5:
            self.region = ScreenRegion(left=left, top=top, width=width, height=height)
        self.window.destroy()

    def _cancel(self, event) -> None:
        self.region = None
        self.window.destroy()


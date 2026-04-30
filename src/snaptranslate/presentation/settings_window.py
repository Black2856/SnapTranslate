from __future__ import annotations

import tkinter as tk
from tkinter import messagebox

from snaptranslate.domain.models import AppSettings, RegionMode


class SettingsWindow:
    def __init__(self, root: tk.Tk, settings: AppSettings, on_save, region_selector) -> None:
        self.root = root
        self.settings = settings
        self.on_save = on_save
        self.region_selector = region_selector
        self.window: tk.Toplevel | None = None

    def show(self) -> None:
        if self.window and self.window.winfo_exists():
            self.window.deiconify()
            self.window.lift()
            return

        self.window = tk.Toplevel(self.root)
        self.window.title("SnapTranslate Settings")
        self.window.geometry("720x680+160+100")

        frame = tk.Frame(self.window)
        frame.pack(fill="both", expand=True, padx=12, pady=12)

        self.read_hotkey = self._entry(frame, "Read hotkey", self.settings.read_hotkey)
        self.input_hotkey = self._entry(frame, "Input hotkey", self.settings.input_hotkey)
        self.model = self._entry(frame, "ChatGPT model", self.settings.chatgpt_model)
        self.ocr_language = self._entry(frame, "PaddleOCR language", self.settings.ocr_language)
        self.text_color = self._entry(frame, "Overlay text color", self.settings.overlay_text_color)
        self.font_family = self._entry(frame, "Overlay font", self.settings.overlay_font_family)
        self.font_size = self._entry(frame, "Overlay font size", str(self.settings.overlay_font_size))

        self.show_status_var = tk.BooleanVar(value=self.settings.show_status)
        tk.Checkbutton(frame, text="Show status", variable=self.show_status_var).pack(anchor="w")
        self.keep_draft_var = tk.BooleanVar(value=self.settings.keep_draft_on_hide)
        tk.Checkbutton(frame, text="Keep input draft on hide", variable=self.keep_draft_var).pack(anchor="w")
        self.history_var = tk.BooleanVar(value=self.settings.enable_history)
        tk.Checkbutton(frame, text="Enable local history JSONL", variable=self.history_var).pack(anchor="w")

        self.region_mode_var = tk.StringVar(value=self.settings.region_mode.value)
        tk.Label(frame, text="Region mode").pack(anchor="w", pady=(8, 0))
        tk.Radiobutton(frame, text="Saved", variable=self.region_mode_var, value=RegionMode.SAVED.value).pack(anchor="w")
        tk.Radiobutton(
            frame,
            text="Interactive drag each time",
            variable=self.region_mode_var,
            value=RegionMode.INTERACTIVE.value,
        ).pack(anchor="w")
        tk.Button(frame, text="Set saved region", command=self._set_region).pack(anchor="w", pady=4)
        self.region_label = tk.Label(frame, text=self._region_text())
        self.region_label.pack(anchor="w")

        tk.Label(frame, text="Read translation prompt").pack(anchor="w", pady=(8, 0))
        self.read_prompt = tk.Text(frame, height=5, wrap="word")
        self.read_prompt.insert("1.0", self.settings.read_translation_prompt)
        self.read_prompt.pack(fill="x")

        tk.Label(frame, text="Input translation prompt").pack(anchor="w", pady=(8, 0))
        self.input_prompt = tk.Text(frame, height=5, wrap="word")
        self.input_prompt.insert("1.0", self.settings.input_translation_prompt)
        self.input_prompt.pack(fill="x")

        buttons = tk.Frame(frame)
        buttons.pack(fill="x", pady=12)
        tk.Button(buttons, text="Save", command=self._save).pack(side="right")

    def _entry(self, parent, label: str, value: str) -> tk.Entry:
        tk.Label(parent, text=label).pack(anchor="w", pady=(6, 0))
        entry = tk.Entry(parent)
        entry.insert(0, value)
        entry.pack(fill="x")
        return entry

    def _set_region(self) -> None:
        region = self.region_selector.select_region()
        if region:
            self.settings.saved_region = region
            self.region_label.configure(text=self._region_text())

    def _region_text(self) -> str:
        region = self.settings.saved_region
        if not region:
            return "Saved region: not set"
        return f"Saved region: {region.left},{region.top} {region.width}x{region.height}"

    def _save(self) -> None:
        try:
            self.settings.read_hotkey = self.read_hotkey.get().strip()
            self.settings.input_hotkey = self.input_hotkey.get().strip()
            self.settings.chatgpt_model = self.model.get().strip()
            self.settings.ocr_language = self.ocr_language.get().strip()
            self.settings.overlay_text_color = self.text_color.get().strip()
            self.settings.overlay_font_family = self.font_family.get().strip()
            self.settings.overlay_font_size = int(self.font_size.get().strip())
            self.settings.show_status = self.show_status_var.get()
            self.settings.keep_draft_on_hide = self.keep_draft_var.get()
            self.settings.enable_history = self.history_var.get()
            self.settings.region_mode = RegionMode(self.region_mode_var.get())
            self.settings.read_translation_prompt = self.read_prompt.get("1.0", "end").strip()
            self.settings.input_translation_prompt = self.input_prompt.get("1.0", "end").strip()
            self.settings.validate()
            self.on_save(self.settings)
            messagebox.showinfo("SnapTranslate", "Settings saved. Restart the app to re-register hotkeys.")
        except Exception as exc:
            messagebox.showerror("SnapTranslate", str(exc))

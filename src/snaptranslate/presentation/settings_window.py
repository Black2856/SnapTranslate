from __future__ import annotations

import tkinter as tk
from tkinter import messagebox

from snaptranslate.domain.models import ApiKeySource, AppSettings, RegionMode


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
        self.window.geometry("760x760+160+80")
        self.window.minsize(640, 520)

        canvas = tk.Canvas(self.window, highlightthickness=0)
        scrollbar = tk.Scrollbar(self.window, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)

        frame = tk.Frame(canvas)
        content_window = canvas.create_window((0, 0), window=frame, anchor="nw")
        frame.bind("<Configure>", lambda event: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.bind("<Configure>", lambda event: canvas.itemconfigure(content_window, width=event.width))

        inner = tk.Frame(frame)
        inner.pack(fill="both", expand=True, padx=12, pady=12)

        self.read_hotkey = self._entry(inner, "Read hotkey", self.settings.read_hotkey)
        self.input_hotkey = self._entry(inner, "Input hotkey", self.settings.input_hotkey)
        self.model = self._entry(inner, "ChatGPT model", self.settings.chatgpt_model)
        self.api_key_source_var = tk.StringVar(value=self.settings.api_key_source.value)
        tk.Label(inner, text="API key source").pack(anchor="w", pady=(8, 0))
        tk.Radiobutton(
            inner,
            text="OPENAI_API_KEY environment variable",
            variable=self.api_key_source_var,
            value=ApiKeySource.ENV.value,
        ).pack(anchor="w")
        tk.Radiobutton(
            inner,
            text="Saved in config.json",
            variable=self.api_key_source_var,
            value=ApiKeySource.CONFIG.value,
        ).pack(anchor="w")
        self.api_key = self._entry(inner, "API key", self.settings.api_key, show="*")
        self.request_timeout = self._entry(
            inner,
            "Request timeout seconds",
            str(self.settings.request_timeout_seconds),
        )
        self.text_color = self._entry(inner, "Overlay text color", self.settings.overlay_text_color)
        self.font_family = self._entry(inner, "Overlay font", self.settings.overlay_font_family)
        self.font_size = self._entry(inner, "Overlay font size", str(self.settings.overlay_font_size))

        self.show_status_var = tk.BooleanVar(value=self.settings.show_status)
        tk.Checkbutton(inner, text="Show status", variable=self.show_status_var).pack(anchor="w")
        self.keep_draft_var = tk.BooleanVar(value=self.settings.keep_draft_on_hide)
        tk.Checkbutton(inner, text="Keep input draft on hide", variable=self.keep_draft_var).pack(anchor="w")
        self.history_var = tk.BooleanVar(value=self.settings.enable_history)
        tk.Checkbutton(inner, text="Enable local history JSONL", variable=self.history_var).pack(anchor="w")

        self.region_mode_var = tk.StringVar(value=self.settings.region_mode.value)
        tk.Label(inner, text="Region mode").pack(anchor="w", pady=(8, 0))
        tk.Radiobutton(inner, text="Saved", variable=self.region_mode_var, value=RegionMode.SAVED.value).pack(anchor="w")
        tk.Radiobutton(
            inner,
            text="Interactive drag each time",
            variable=self.region_mode_var,
            value=RegionMode.INTERACTIVE.value,
        ).pack(anchor="w")
        tk.Button(inner, text="Set saved region", command=self._set_region).pack(anchor="w", pady=4)
        self.region_label = tk.Label(inner, text=self._region_text())
        self.region_label.pack(anchor="w")

        tk.Label(inner, text="Read image translation prompt").pack(anchor="w", pady=(8, 0))
        self.read_prompt = tk.Text(inner, height=7, wrap="word")
        self.read_prompt.insert("1.0", self.settings.read_image_prompt)
        self.read_prompt.pack(fill="x")

        tk.Label(inner, text="Input translation prompt").pack(anchor="w", pady=(8, 0))
        self.input_prompt = tk.Text(inner, height=7, wrap="word")
        self.input_prompt.insert("1.0", self.settings.input_translation_prompt)
        self.input_prompt.pack(fill="x")

        buttons = tk.Frame(inner)
        buttons.pack(fill="x", pady=12)
        tk.Button(buttons, text="Save", command=self._save).pack(side="right")

    def _entry(self, parent, label: str, value: str, show: str | None = None) -> tk.Entry:
        tk.Label(parent, text=label).pack(anchor="w", pady=(6, 0))
        entry = tk.Entry(parent, show=show)
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
            self.settings.api_key_source = ApiKeySource(self.api_key_source_var.get())
            self.settings.api_key = self.api_key.get().strip()
            self.settings.request_timeout_seconds = float(self.request_timeout.get().strip())
            self.settings.overlay_text_color = self.text_color.get().strip()
            self.settings.overlay_font_family = self.font_family.get().strip()
            self.settings.overlay_font_size = int(self.font_size.get().strip())
            self.settings.show_status = self.show_status_var.get()
            self.settings.keep_draft_on_hide = self.keep_draft_var.get()
            self.settings.enable_history = self.history_var.get()
            self.settings.region_mode = RegionMode(self.region_mode_var.get())
            self.settings.read_image_prompt = self.read_prompt.get("1.0", "end").strip()
            self.settings.input_translation_prompt = self.input_prompt.get("1.0", "end").strip()
            self.settings.validate()
            self.on_save(self.settings)
            messagebox.showinfo("SnapTranslate", "Settings saved. Restart the app to re-register hotkeys.")
        except Exception as exc:
            messagebox.showerror("SnapTranslate", str(exc))

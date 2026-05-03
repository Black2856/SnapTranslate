from __future__ import annotations

import tkinter as tk
from tkinter import messagebox, ttk

from snaptranslate.domain.models import (
    ApiKeySource,
    AppSettings,
    ReadResultDisplayMode,
    RegionMode,
    UiLanguage,
)


TEXT = {
    "en": {
        "title": "SnapTranslate Settings",
        "tab_general": "General",
        "tab_api": "API",
        "tab_read": "Read",
        "tab_overlay": "Overlay",
        "tab_history": "History",
        "tab_prompts": "Prompts",
        "ui_language": "UI language",
        "language_en": "English",
        "language_ja": "Japanese",
        "read_hotkey": "Read hotkey",
        "input_hotkey": "Input hotkey",
        "read_box_color": "Read box color",
        "keep_draft": "Keep input draft on hide",
        "model": "ChatGPT model",
        "api_key_source": "API key source",
        "api_env": "OPENAI_API_KEY environment variable",
        "api_config": "Saved in config.json",
        "api_key": "API key",
        "request_timeout": "Request timeout seconds",
        "region_mode": "Region mode",
        "region_saved": "Saved",
        "region_interactive": "Interactive drag each time",
        "set_region": "Set saved region",
        "saved_region_missing": "Saved region: not set",
        "saved_region": "Saved region: {left},{top} {width}x{height}",
        "read_result_display": "Read result display",
        "display_overlay": "Overlay on captured region",
        "display_window": "Normal window",
        "overlay_color": "Overlay text color",
        "overlay_font": "Overlay font",
        "overlay_font_size": "Overlay font size",
        "show_status": "Show status",
        "history": "Enable local history JSONL",
        "read_prompt": "Read image translation prompt",
        "input_prompt": "Input translation prompt",
        "save": "Save",
        "saved_message": "Settings saved. Restart the app to re-register hotkeys.",
    },
    "ja": {
        "title": "SnapTranslate 設定",
        "tab_general": "一般",
        "tab_api": "API",
        "tab_read": "読み取り",
        "tab_overlay": "表示",
        "tab_history": "履歴",
        "tab_prompts": "プロンプト",
        "ui_language": "表示言語",
        "language_en": "英語",
        "language_ja": "日本語",
        "read_hotkey": "読み取りホットキー",
        "input_hotkey": "入力ホットキー",
        "read_box_color": "読み取りボックス色",
        "keep_draft": "非表示時に入力途中のテキストを保持",
        "model": "ChatGPT モデル",
        "api_key_source": "APIキーの取得元",
        "api_env": "OPENAI_API_KEY 環境変数",
        "api_config": "config.json に保存",
        "api_key": "APIキー",
        "request_timeout": "リクエストタイムアウト秒数",
        "region_mode": "範囲選択モード",
        "region_saved": "保存済み範囲",
        "region_interactive": "毎回ドラッグして選択",
        "set_region": "保存範囲を設定",
        "saved_region_missing": "保存範囲: 未設定",
        "saved_region": "保存範囲: {left},{top} {width}x{height}",
        "read_result_display": "読み取り結果の表示方法",
        "display_overlay": "キャプチャ範囲に重ねて表示",
        "display_window": "通常ウィンドウ",
        "overlay_color": "オーバーレイ文字色",
        "overlay_font": "オーバーレイフォント",
        "overlay_font_size": "オーバーレイフォントサイズ",
        "show_status": "ステータスを表示",
        "history": "ローカル履歴JSONLを有効化",
        "read_prompt": "画像読み取り翻訳プロンプト",
        "input_prompt": "入力翻訳プロンプト",
        "save": "保存",
        "saved_message": "設定を保存しました。ホットキーを再登録するにはアプリを再起動してください。",
    },
}

TOOLTIPS = {
    "en": {
        "ui_language": "Changes the language used in this settings window after saving and reopening it.",
        "read_hotkey": "Starts image translation. If the overlay is visible, the same hotkey hides it.",
        "input_hotkey": "Shows or hides the manual text input window.",
        "read_box_color": "Background color for the read translation result box. Use a hex color such as #000000.",
        "keep_draft": "Keeps typed text in the input window when the window is hidden.",
        "model": "OpenAI model used for both image and manual text translation.",
        "api_key_source": "Choose whether the API key comes from the environment or this config file.",
        "api_key": "Used only when API key source is set to config.json. Do not share this file.",
        "request_timeout": "Maximum number of seconds to wait for an OpenAI API response.",
        "region_mode": "Saved uses one registered rectangle. Interactive asks you to drag a region every time.",
        "set_region": "Drag on the screen to save the region used by Saved mode.",
        "read_result_display": "Controls whether image translation results appear as an overlay or a normal window.",
        "overlay_color": "Hex color used for overlay text, for example #FFFFFF.",
        "overlay_font": "Windows font family used for overlay text, for example Yu Gothic UI.",
        "overlay_font_size": "Overlay text size in points.",
        "show_status": "Shows a small status indicator such as [read]: translating.",
        "history": "Writes translation history to %APPDATA%/SnapTranslate/history.jsonl.",
        "read_prompt": "Prompt sent with screenshots. Keep it focused on reading and translating image text.",
        "input_prompt": "Prompt template for typed text translation. Keep {text} where the input should be inserted.",
    },
    "ja": {
        "ui_language": "保存して設定画面を開き直した後、この設定画面の表示言語を切り替えます。",
        "read_hotkey": "画像翻訳を開始します。結果表示中は同じホットキーで非表示にします。",
        "input_hotkey": "手入力翻訳ウィンドウを表示または非表示にします。",
        "read_box_color": "読み取り翻訳結果を表示するボックスの背景色です。#000000 のようなHEX色を入力してください。",
        "keep_draft": "入力ウィンドウを閉じても、入力途中のテキストを残します。",
        "model": "画像翻訳と手入力翻訳の両方で使うOpenAIモデルです。",
        "api_key_source": "APIキーを環境変数から読むか、設定ファイルから読むかを選びます。",
        "api_key": "config.jsonに保存する場合だけ使います。このファイルは共有しないでください。",
        "request_timeout": "OpenAI APIの応答を待つ最大秒数です。",
        "region_mode": "保存済み範囲を使うか、毎回ドラッグで範囲を選ぶかを指定します。",
        "set_region": "画面上をドラッグして、保存済み範囲として登録します。",
        "read_result_display": "画像翻訳結果をオーバーレイで出すか、通常ウィンドウで出すかを選びます。",
        "overlay_color": "オーバーレイ文字の色です。例: #FFFFFF。",
        "overlay_font": "オーバーレイ文字に使うWindowsフォント名です。例: Yu Gothic UI。",
        "overlay_font_size": "オーバーレイ文字のポイントサイズです。",
        "show_status": "[read]: translating などの小さなステータス表示を出します。",
        "history": "翻訳履歴を %APPDATA%/SnapTranslate/history.jsonl に保存します。",
        "read_prompt": "スクリーンショットと一緒に送るプロンプトです。画像内テキストの読み取りと翻訳に絞ってください。",
        "input_prompt": "手入力翻訳用のプロンプトです。入力文を挿入する位置に {text} を残してください。",
    },
}


class ToolTip:
    def __init__(self, widget: tk.Widget, text: str) -> None:
        self.widget = widget
        self.text = text
        self.window: tk.Toplevel | None = None
        self.widget.bind("<Enter>", self._show, add="+")
        self.widget.bind("<Leave>", self._hide, add="+")

    def _show(self, _event) -> None:
        if self.window or not self.text:
            return
        x = self.widget.winfo_rootx() + 18
        y = self.widget.winfo_rooty() + self.widget.winfo_height() + 4
        self.window = tk.Toplevel(self.widget)
        self.window.wm_overrideredirect(True)
        self.window.wm_geometry(f"+{x}+{y}")
        label = tk.Label(
            self.window,
            text=self.text,
            justify="left",
            wraplength=360,
            background="#ffffe0",
            relief="solid",
            borderwidth=1,
            padx=6,
            pady=4,
        )
        label.pack()

    def _hide(self, _event) -> None:
        if self.window:
            self.window.destroy()
            self.window = None


class SettingsWindow:
    def __init__(self, root: tk.Tk, settings: AppSettings, on_save, region_selector) -> None:
        self.root = root
        self.settings = settings
        self.on_save = on_save
        self.region_selector = region_selector
        self.window: tk.Toplevel | None = None
        self.language = settings.ui_language.value
        self.language_values: dict[str, str] = {}
        self.language_display_to_value: dict[str, str] = {}

    def show(self) -> None:
        if self.window and self.window.winfo_exists():
            self.window.deiconify()
            self.window.lift()
            return

        self.language = self.settings.ui_language.value
        self.window = tk.Toplevel(self.root)
        self.window.title(self._text("title"))
        self.window.geometry("820x720+160+80")
        self.window.minsize(680, 520)

        notebook = ttk.Notebook(self.window)
        notebook.pack(fill="both", expand=True, padx=12, pady=(12, 0))

        general = self._tab(notebook, "tab_general")
        api = self._tab(notebook, "tab_api")
        read = self._tab(notebook, "tab_read")
        overlay = self._tab(notebook, "tab_overlay")
        history = self._tab(notebook, "tab_history")
        prompts = self._tab(notebook, "tab_prompts")

        self.language_values = {
            self._text("language_en"): UiLanguage.EN.value,
            self._text("language_ja"): UiLanguage.JA.value,
        }
        self.language_display_to_value = dict(self.language_values)
        language_value_to_display = {value: label for label, value in self.language_values.items()}
        self.ui_language_var = tk.StringVar(
            value=language_value_to_display[self.settings.ui_language.value]
        )
        self._combobox(general, "ui_language", self.ui_language_var, list(self.language_values))
        self.read_hotkey = self._entry(general, "read_hotkey", self.settings.read_hotkey)
        self.input_hotkey = self._entry(general, "input_hotkey", self.settings.input_hotkey)
        self.keep_draft_var = tk.BooleanVar(value=self.settings.keep_draft_on_hide)
        self._checkbutton(general, "keep_draft", self.keep_draft_var)

        self.model = self._entry(api, "model", self.settings.chatgpt_model)
        self.api_key_source_var = tk.StringVar(value=self.settings.api_key_source.value)
        self._label(api, "api_key_source", pady=(8, 0))
        self._radiobutton(api, "api_env", self.api_key_source_var, ApiKeySource.ENV.value, "api_key_source")
        self._radiobutton(
            api,
            "api_config",
            self.api_key_source_var,
            ApiKeySource.CONFIG.value,
            "api_key_source",
        )
        self.api_key = self._entry(api, "api_key", self.settings.api_key, show="*")
        self.request_timeout = self._entry(
            api,
            "request_timeout",
            str(self.settings.request_timeout_seconds),
        )

        self.region_mode_var = tk.StringVar(value=self.settings.region_mode.value)
        self._label(read, "region_mode", pady=(8, 0))
        self._radiobutton(read, "region_saved", self.region_mode_var, RegionMode.SAVED.value, "region_mode")
        self._radiobutton(
            read,
            "region_interactive",
            self.region_mode_var,
            RegionMode.INTERACTIVE.value,
            "region_mode",
        )
        self._button(read, "set_region", self._set_region).pack(anchor="w", pady=4)
        self.region_label = tk.Label(read, text=self._region_text())
        self.region_label.pack(anchor="w")

        self.read_result_display_mode_var = tk.StringVar(
            value=self.settings.read_result_display_mode.value
        )
        self._label(overlay, "read_result_display", pady=(8, 0))
        self._radiobutton(
            overlay,
            "display_overlay",
            self.read_result_display_mode_var,
            ReadResultDisplayMode.OVERLAY.value,
            "read_result_display",
        )
        self._radiobutton(
            overlay,
            "display_window",
            self.read_result_display_mode_var,
            ReadResultDisplayMode.WINDOW.value,
            "read_result_display",
        )
        self.text_color = self._entry(overlay, "overlay_color", self.settings.overlay_text_color)
        self.read_box_color = self._entry(overlay, "read_box_color", self.settings.read_box_color)
        self.font_family = self._entry(overlay, "overlay_font", self.settings.overlay_font_family)
        self.font_size = self._entry(overlay, "overlay_font_size", str(self.settings.overlay_font_size))
        self.show_status_var = tk.BooleanVar(value=self.settings.show_status)
        self._checkbutton(overlay, "show_status", self.show_status_var)

        self.history_var = tk.BooleanVar(value=self.settings.enable_history)
        self._checkbutton(history, "history", self.history_var)

        self._label(prompts, "read_prompt", pady=(8, 0))
        self.read_prompt = tk.Text(prompts, height=9, wrap="word")
        self.read_prompt.insert("1.0", self.settings.read_image_prompt)
        self.read_prompt.pack(fill="both", expand=True)
        ToolTip(self.read_prompt, self._tooltip("read_prompt"))

        self._label(prompts, "input_prompt", pady=(8, 0))
        self.input_prompt = tk.Text(prompts, height=9, wrap="word")
        self.input_prompt.insert("1.0", self.settings.input_translation_prompt)
        self.input_prompt.pack(fill="both", expand=True)
        ToolTip(self.input_prompt, self._tooltip("input_prompt"))

        buttons = tk.Frame(self.window)
        buttons.pack(fill="x", padx=12, pady=12)
        self._button(buttons, "save", self._save).pack(side="right")

    def _tab(self, notebook: ttk.Notebook, key: str) -> tk.Frame:
        frame = tk.Frame(notebook)
        inner = tk.Frame(frame)
        inner.pack(fill="both", expand=True, padx=12, pady=12)
        notebook.add(frame, text=self._text(key))
        return inner

    def _text(self, key: str) -> str:
        return TEXT[self.language][key]

    def _tooltip(self, key: str) -> str:
        return TOOLTIPS[self.language][key]

    def _label(self, parent, key: str, pady=(6, 0)) -> tk.Label:
        label = tk.Label(parent, text=self._text(key))
        label.pack(anchor="w", pady=pady)
        ToolTip(label, self._tooltip(key))
        return label

    def _entry(self, parent, key: str, value: str, show: str | None = None) -> tk.Entry:
        self._label(parent, key)
        entry = tk.Entry(parent, show=show)
        entry.insert(0, value)
        entry.pack(fill="x")
        ToolTip(entry, self._tooltip(key))
        return entry

    def _combobox(self, parent, key: str, variable: tk.StringVar, values: list[str]) -> ttk.Combobox:
        self._label(parent, key)
        combo = ttk.Combobox(parent, textvariable=variable, values=values, state="readonly")
        combo.pack(fill="x")
        ToolTip(combo, self._tooltip(key))
        return combo

    def _checkbutton(self, parent, key: str, variable: tk.BooleanVar) -> tk.Checkbutton:
        button = tk.Checkbutton(parent, text=self._text(key), variable=variable)
        button.pack(anchor="w", pady=(8, 0))
        ToolTip(button, self._tooltip(key))
        return button

    def _radiobutton(
        self,
        parent,
        text_key: str,
        variable: tk.StringVar,
        value: str,
        tooltip_key: str,
    ) -> tk.Radiobutton:
        button = tk.Radiobutton(
            parent,
            text=self._text(text_key),
            variable=variable,
            value=value,
        )
        button.pack(anchor="w")
        ToolTip(button, self._tooltip(tooltip_key))
        return button

    def _button(self, parent, key: str, command) -> tk.Button:
        button = tk.Button(parent, text=self._text(key), command=command)
        if key in TOOLTIPS[self.language]:
            ToolTip(button, self._tooltip(key))
        return button

    def _set_region(self) -> None:
        region = self.region_selector.select_region()
        if region:
            self.settings.saved_region = region
            self.region_label.configure(text=self._region_text())

    def _region_text(self) -> str:
        region = self.settings.saved_region
        if not region:
            return self._text("saved_region_missing")
        return self._text("saved_region").format(
            left=region.left,
            top=region.top,
            width=region.width,
            height=region.height,
        )

    def _save(self) -> None:
        try:
            self.settings.ui_language = UiLanguage(
                self.language_display_to_value[self.ui_language_var.get()]
            )
            self.settings.read_hotkey = self.read_hotkey.get().strip()
            self.settings.input_hotkey = self.input_hotkey.get().strip()
            self.settings.chatgpt_model = self.model.get().strip()
            self.settings.api_key_source = ApiKeySource(self.api_key_source_var.get())
            self.settings.api_key = self.api_key.get().strip()
            self.settings.request_timeout_seconds = float(self.request_timeout.get().strip())
            self.settings.overlay_text_color = self.text_color.get().strip()
            self.settings.read_box_color = self.read_box_color.get().strip()
            self.settings.overlay_font_family = self.font_family.get().strip()
            self.settings.overlay_font_size = int(self.font_size.get().strip())
            self.settings.read_result_display_mode = ReadResultDisplayMode(
                self.read_result_display_mode_var.get()
            )
            self.settings.show_status = self.show_status_var.get()
            self.settings.keep_draft_on_hide = self.keep_draft_var.get()
            self.settings.enable_history = self.history_var.get()
            self.settings.region_mode = RegionMode(self.region_mode_var.get())
            self.settings.read_image_prompt = self.read_prompt.get("1.0", "end").strip()
            self.settings.input_translation_prompt = self.input_prompt.get("1.0", "end").strip()
            self.settings.validate()
            self.on_save(self.settings)
            messagebox.showinfo("SnapTranslate", self._text("saved_message"))
        except Exception as exc:
            messagebox.showerror("SnapTranslate", str(exc))

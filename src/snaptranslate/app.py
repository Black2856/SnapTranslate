from __future__ import annotations

import logging
import threading
import tkinter as tk

from snaptranslate.application.hotkey_controller import HotkeyController
from snaptranslate.application.input_translate_usecase import InputTranslateUseCase
from snaptranslate.application.read_translate_usecase import ReadTranslateUseCase
from snaptranslate.domain.models import AppSettings, RegionMode
from snaptranslate.domain.state import AppState
from snaptranslate.infrastructure.clipboard import ClipboardService
from snaptranslate.infrastructure.config_store import ConfigStore
from snaptranslate.infrastructure.history_store import HistoryStore
from snaptranslate.infrastructure.screenshot import ScreenshotService
from snaptranslate.infrastructure.translator import ChatGptTranslator
from snaptranslate.presentation.input_window import InputWindow
from snaptranslate.presentation.overlay_window import OverlayWindow
from snaptranslate.presentation.region_selector import RegionSelector
from snaptranslate.presentation.settings_window import SettingsWindow
from snaptranslate.presentation.status_window import StatusWindow
from snaptranslate.presentation.tray_icon import TrayIcon

logger = logging.getLogger(__name__)


class SnapTranslateApp:
    def __init__(self, config_store: ConfigStore | None = None) -> None:
        self.config_store = config_store or ConfigStore()
        self.settings: AppSettings = self.config_store.load()
        self.state = AppState()
        self.root = tk.Tk()
        self.root.withdraw()
        self.status_window = StatusWindow(self.root, visible=self.settings.show_status)
        self.overlay_window = OverlayWindow(self.root)
        self.region_selector = RegionSelector(self.root)
        self.input_window: InputWindow | None = None
        self.settings_window: SettingsWindow | None = None
        self.hotkeys: HotkeyController | None = None
        self.tray: TrayIcon | None = None
        self._read_launch_lock = threading.Lock()
        self._read_launch_active = False
        self._wire()

    def _wire(self) -> None:
        translator = ChatGptTranslator(self.settings)
        history_store = HistoryStore(self.settings.history_path)
        self.input_window = InputWindow(self.root, on_submit=self._run_input_translate)
        self.input_usecase = InputTranslateUseCase(
            settings=self.settings,
            state=self.state,
            translator=translator,
            clipboard_service=ClipboardService(),
            input_window=self.input_window,
            status_window=self.status_window,
            history_store=history_store,
        )
        self.read_usecase = ReadTranslateUseCase(
            settings=self.settings,
            state=self.state,
            region_selector=self.region_selector,
            screenshot_service=ScreenshotService(),
            translator=translator,
            overlay_window=self.overlay_window,
            status_window=self.status_window,
            history_store=history_store,
        )
        self.settings_window = SettingsWindow(
            self.root,
            self.settings,
            on_save=self._save_settings,
            region_selector=self.region_selector,
        )
        self.hotkeys = HotkeyController(
            self.settings.read_hotkey,
            self.settings.input_hotkey,
            on_read=lambda: self.root.after(0, self._run_read_translate),
            on_input=lambda: self.root.after(0, self.input_usecase.toggle_input_window),
        )
        self.tray = TrayIcon(
            on_settings=lambda: self.root.after(0, self.settings_window.show),
            on_quit=lambda: self.root.after(0, self.stop),
        )

    def start(self) -> None:
        assert self.hotkeys is not None
        assert self.tray is not None
        self.hotkeys.start()
        self.tray.start()
        self.status_window.set_message("[ready]")
        self.root.mainloop()

    def stop(self) -> None:
        if self.hotkeys:
            self.hotkeys.stop()
        self.root.quit()
        self.root.destroy()

    def _save_settings(self, settings: AppSettings) -> None:
        self.config_store.save(settings)
        self.settings = settings
        self.status_window.set_visible(settings.show_status)

    def _run_read_translate(self) -> None:
        if self.state.snapshot().read.value == "overlay_visible":
            self.read_usecase.toggle_or_run()
            return
        if not self._begin_read_launch():
            self.status_window.set_message("[read]: busy")
            return
        region = None
        if self.settings.region_mode == RegionMode.INTERACTIVE:
            region = self.region_selector.select_region()
            if region is None:
                self.status_window.set_message("[read]: canceled")
                self._finish_read_launch()
                return
        threading.Thread(
            target=lambda: self._run_read_translate_worker(region),
            name="read-translate",
            daemon=True,
        ).start()

    def _run_input_translate(self, source: str) -> None:
        threading.Thread(target=lambda: self.input_usecase.translate_text(source), name="input-translate", daemon=True).start()

    def _begin_read_launch(self) -> bool:
        with self._read_launch_lock:
            if self._read_launch_active or self.state.is_read_busy():
                return False
            self._read_launch_active = True
            return True

    def _finish_read_launch(self) -> None:
        with self._read_launch_lock:
            self._read_launch_active = False

    def _run_read_translate_worker(self, region) -> None:
        try:
            self.read_usecase.run(region_override=region)
        finally:
            self._finish_read_launch()

from __future__ import annotations

import logging
from datetime import datetime, timezone

from snaptranslate.domain.models import AppSettings, HistoryEntry, RegionMode
from snaptranslate.domain.state import AppState, ReadState

logger = logging.getLogger(__name__)


class ReadTranslateUseCase:
    def __init__(
        self,
        settings: AppSettings,
        state: AppState,
        region_selector,
        screenshot_service,
        ocr_service,
        translator,
        overlay_window,
        status_window,
        history_store=None,
    ) -> None:
        self.settings = settings
        self.state = state
        self.region_selector = region_selector
        self.screenshot_service = screenshot_service
        self.ocr_service = ocr_service
        self.translator = translator
        self.overlay_window = overlay_window
        self.status_window = status_window
        self.history_store = history_store

    def toggle_or_run(self) -> None:
        snapshot = self.state.snapshot()
        if snapshot.read == ReadState.OVERLAY_VISIBLE:
            self.overlay_window.hide()
            self.state.set_read(ReadState.IDLE, "[read]: idle")
            self.status_window.set_message("[read]: idle")
            return
        self.run()

    def run(self, region_override=None) -> None:
        if self.state.is_read_busy():
            return

        try:
            self.state.set_read(ReadState.REGION_SELECTING, "[read]: selecting")
            self.status_window.set_message("[read]: selecting")
            region = region_override or self._get_region()
            if region is None:
                raise RuntimeError("OCR region is not set.")

            self.state.set_read(ReadState.OCR_RUNNING, "[read]: OCR")
            self.status_window.set_message("[read]: OCR")
            image = self.screenshot_service.capture(region)
            ocr_result = self.ocr_service.extract_text(image)
            if not ocr_result.text.strip():
                raise RuntimeError("OCR result was empty.")

            self.state.set_read(ReadState.TRANSLATING, "[read]: translating")
            self.status_window.set_message("[read]: translating")
            result = self.translator.translate(ocr_result.text, self.settings.read_translation_prompt)

            self.overlay_window.show_text(result.text, region, self.settings)
            self.state.set_read(ReadState.OVERLAY_VISIBLE, "[read]: visible")
            self.status_window.set_message("[read]: visible")
            self._append_history("read", ocr_result.text, result.text, result.model)
        except Exception as exc:
            logger.exception("Read translation failed")
            self.state.set_read(ReadState.ERROR, "[read]: error")
            self.status_window.set_message(f"[read]: {exc}")

    def _get_region(self):
        if self.settings.region_mode == RegionMode.SAVED:
            return self.settings.saved_region
        return self.region_selector.select_region()

    def _append_history(self, mode: str, source: str, translated: str, model: str) -> None:
        if not self.settings.enable_history or not self.history_store:
            return
        self.history_store.append(
            HistoryEntry(
                timestamp=datetime.now(timezone.utc).isoformat(),
                mode=mode,
                source_text=source,
                translated_text=translated,
                model=model,
            )
        )

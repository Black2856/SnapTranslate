from __future__ import annotations

import logging
from datetime import datetime, timezone
from threading import Lock

from snaptranslate.domain.models import AppSettings, HistoryEntry, RegionMode
from snaptranslate.domain.state import AppState, ReadState
from snaptranslate.application.timeout import run_with_timeout
from snaptranslate.presentation.markup import normalize_markup

logger = logging.getLogger(__name__)


class ReadTranslateUseCase:
    def __init__(
        self,
        settings: AppSettings,
        state: AppState,
        region_selector,
        screenshot_service,
        translator,
        overlay_window,
        status_window,
        history_store=None,
    ) -> None:
        self.settings = settings
        self.state = state
        self.region_selector = region_selector
        self.screenshot_service = screenshot_service
        self.translator = translator
        self.overlay_window = overlay_window
        self.status_window = status_window
        self.history_store = history_store
        self._run_lock = Lock()

    def toggle_or_run(self) -> None:
        snapshot = self.state.snapshot()
        if snapshot.read == ReadState.OVERLAY_VISIBLE:
            self.overlay_window.hide()
            self.state.set_read(ReadState.IDLE, "[read]: idle")
            self.status_window.set_message("[read]: idle")
            return
        self.run()

    def run(self, region_override=None) -> None:
        if not self._run_lock.acquire(blocking=False):
            self.status_window.set_message("[read]: busy")
            return
        try:
            self._run_locked(region_override=region_override)
        finally:
            self._run_lock.release()

    def _run_locked(self, region_override=None) -> None:
        if self.state.is_read_busy():
            self.status_window.set_message("[read]: busy")
            return

        try:
            self.state.set_read(ReadState.REGION_SELECTING, "[read]: selecting")
            self.status_window.set_message("[read]: selecting")
            region = region_override or self._get_region()
            if region is None:
                raise RuntimeError("Read region is not set.")

            self.state.set_read(ReadState.CAPTURING, "[read]: capturing")
            self.status_window.set_message("[read]: capturing")
            image = self.screenshot_service.capture(region)

            self.state.set_read(ReadState.ANALYZING, "[read]: analyzing")
            self.status_window.set_message("[read]: analyzing")
            result = self._translate_image_with_timeout(image)
            translated_text = normalize_markup(result.text)
            if not translated_text.strip():
                raise RuntimeError("Image translation response was empty.")

            self.overlay_window.show_text(translated_text, region, self.settings)
            self.state.set_read(ReadState.OVERLAY_VISIBLE, "[read]: visible")
            self.status_window.set_message("[read]: visible")
            self._append_history(
                mode="read",
                source="[image]",
                translated=translated_text,
                model=result.model,
                metadata={
                    "region": {
                        "left": region.left,
                        "top": region.top,
                        "width": region.width,
                        "height": region.height,
                    },
                    "image_size": {"width": image.width, "height": image.height},
                },
            )
        except Exception as exc:
            logger.exception("Read translation failed")
            self.state.set_read(ReadState.ERROR, "[read]: error")
            self.status_window.set_message(f"[read]: {exc}")

    def _translate_image_with_timeout(self, image):
        return run_with_timeout(
            lambda: self.translator.translate_image(image, self.settings.read_image_prompt),
            self.settings.request_timeout_seconds,
            f"Read translation timed out after {self.settings.request_timeout_seconds} seconds.",
        )

    def _get_region(self):
        if self.settings.region_mode == RegionMode.SAVED:
            return self.settings.saved_region
        return self.region_selector.select_region()

    def _append_history(
        self,
        mode: str,
        source: str,
        translated: str,
        model: str,
        metadata: dict | None = None,
    ) -> None:
        if not self.settings.enable_history or not self.history_store:
            return
        self.history_store.append(
            HistoryEntry(
                timestamp=datetime.now(timezone.utc).isoformat(),
                mode=mode,
                source_text=source,
                translated_text=translated,
                model=model,
                metadata=metadata or {},
            )
        )

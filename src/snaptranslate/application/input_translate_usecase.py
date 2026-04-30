from __future__ import annotations

import logging
from datetime import datetime, timezone
from threading import Lock

from snaptranslate.domain.models import AppSettings, HistoryEntry
from snaptranslate.domain.state import AppState, InputState

logger = logging.getLogger(__name__)


class InputTranslateUseCase:
    def __init__(
        self,
        settings: AppSettings,
        state: AppState,
        translator,
        clipboard_service,
        input_window,
        status_window,
        history_store=None,
    ) -> None:
        self.settings = settings
        self.state = state
        self.translator = translator
        self.clipboard_service = clipboard_service
        self.input_window = input_window
        self.status_window = status_window
        self.history_store = history_store
        self._lock = Lock()
        self._active = False

    def toggle_input_window(self) -> None:
        if self.input_window.is_visible():
            self.input_window.hide(keep_draft=self.settings.keep_draft_on_hide)
            self.state.set_input(InputState.HIDDEN, "[input]: hidden")
            self.status_window.set_message("[input]: hidden")
            return
        self.input_window.show()
        self.state.set_input(InputState.VISIBLE, "[input]: visible")
        self.status_window.set_message("[input]: visible")

    def translate_current_text(self) -> None:
        if not self._begin_translation():
            return

        source = self.input_window.get_text().strip()
        if not source:
            self._finish_translation()
            self.status_window.set_message("[input]: empty")
            return

        try:
            self.state.set_input(InputState.TRANSLATING, "[input]: translating")
            self.status_window.set_message("[input]: translating")
            result = self.translator.translate(source, self.settings.input_translation_prompt)
            self.clipboard_service.copy_text(result.text)
            self.state.set_input(InputState.COPIED, "[input]: copied")
            self.status_window.set_message("[input]: copied")
            self.input_window.mark_copied()
            self._append_history("input", source, result.text, result.model)
        except Exception as exc:
            logger.exception("Input translation failed")
            self.state.set_input(InputState.ERROR, "[input]: error")
            self.status_window.set_message(f"[input]: {exc}")
            self.input_window.mark_error(str(exc))
        finally:
            self._finish_translation()

    def _begin_translation(self) -> bool:
        with self._lock:
            if self._active:
                self.state.set_input(InputState.TRANSLATING, "[input]: busy")
                self.status_window.set_message("[input]: busy")
                return False
            self._active = True
            return True

    def _finish_translation(self) -> None:
        with self._lock:
            self._active = False

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

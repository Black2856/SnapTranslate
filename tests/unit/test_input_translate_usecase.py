from __future__ import annotations

import threading

from snaptranslate.application.input_translate_usecase import InputTranslateUseCase
from snaptranslate.domain.models import AppSettings, TranslationResult
from snaptranslate.domain.state import AppState


class FakeTranslator:
    def translate(self, text: str, prompt: str) -> TranslationResult:
        return TranslationResult(text=f"translated:{text}", model="fake")


class FakeClipboard:
    def __init__(self) -> None:
        self.value = ""

    def copy_text(self, text: str) -> None:
        self.value = text


class FakeInputWindow:
    def __init__(self, text: str) -> None:
        self.text = text
        self.copied = False
        self.canceled = False
        self.error = ""

    def get_text(self) -> str:
        return self.text

    def mark_copied(self) -> None:
        self.copied = True

    def mark_canceled(self) -> None:
        self.canceled = True

    def mark_error(self, message: str) -> None:
        self.error = message


class FakeStatus:
    def __init__(self) -> None:
        self.messages: list[str] = []

    def set_message(self, message: str) -> None:
        self.messages.append(message)


def test_input_translation_copies_result() -> None:
    clipboard = FakeClipboard()
    input_window = FakeInputWindow("hello")
    status = FakeStatus()
    usecase = InputTranslateUseCase(
        settings=AppSettings(),
        state=AppState(),
        translator=FakeTranslator(),
        clipboard_service=clipboard,
        input_window=input_window,
        status_window=status,
    )

    usecase.translate_current_text()

    assert clipboard.value == "translated:hello"
    assert input_window.copied is True
    assert status.messages[-1] == "[input]: copied"


def test_input_translation_second_run_cancels_active_translation() -> None:
    started = threading.Event()
    release = threading.Event()

    class SlowTranslator:
        def translate(self, text: str, prompt: str) -> TranslationResult:
            started.set()
            release.wait(timeout=5)
            return TranslationResult(text=f"translated:{text}", model="fake")

    clipboard = FakeClipboard()
    input_window = FakeInputWindow("hello")
    status = FakeStatus()
    usecase = InputTranslateUseCase(
        settings=AppSettings(),
        state=AppState(),
        translator=SlowTranslator(),
        clipboard_service=clipboard,
        input_window=input_window,
        status_window=status,
    )

    worker = threading.Thread(target=usecase.translate_current_text)
    worker.start()
    assert started.wait(timeout=5)

    usecase.translate_current_text()
    release.set()
    worker.join(timeout=5)

    assert clipboard.value == ""
    assert input_window.canceled is True
    assert "[input]: canceled" in status.messages

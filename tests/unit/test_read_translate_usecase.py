from __future__ import annotations

import threading

from PIL import Image

from snaptranslate.application.read_translate_usecase import ReadTranslateUseCase
from snaptranslate.domain.models import AppSettings, ScreenRegion, TranslationResult
from snaptranslate.domain.state import AppState, ReadState


class FakeScreenshot:
    def capture(self, region: ScreenRegion) -> Image.Image:
        return Image.new("RGB", (region.width, region.height), "white")


class FakeOverlay:
    def __init__(self) -> None:
        self.text = ""

    def show_text(self, text: str, region: ScreenRegion, settings: AppSettings) -> None:
        self.text = text

    def hide(self) -> None:
        self.text = ""


class FakeStatus:
    def __init__(self) -> None:
        self.messages: list[str] = []

    def set_message(self, message: str) -> None:
        self.messages.append(message)


def test_read_translation_duplicate_run_is_blocked() -> None:
    started = threading.Event()
    release = threading.Event()

    class SlowTranslator:
        def translate_image(self, image: Image.Image, prompt: str) -> TranslationResult:
            started.set()
            release.wait(timeout=5)
            return TranslationResult("translated", "fake")

    status = FakeStatus()
    overlay = FakeOverlay()
    usecase = ReadTranslateUseCase(
        settings=AppSettings(saved_region=ScreenRegion(0, 0, 100, 50)),
        state=AppState(),
        region_selector=None,
        screenshot_service=FakeScreenshot(),
        translator=SlowTranslator(),
        overlay_window=overlay,
        status_window=status,
    )

    worker = threading.Thread(target=usecase.run)
    worker.start()
    assert started.wait(timeout=5)

    usecase.run()
    release.set()
    worker.join(timeout=5)

    assert status.messages.count("[read]: analyzing") == 1
    assert "[read]: busy" in status.messages
    assert overlay.text == "translated"


def test_read_translation_timeout_releases_busy_state() -> None:
    class HangingThenWorkingTranslator:
        def __init__(self) -> None:
            self.calls = 0
            self.started = threading.Event()

        def translate_image(self, image: Image.Image, prompt: str) -> TranslationResult:
            self.calls += 1
            if self.calls == 1:
                self.started.set()
                threading.Event().wait()
            return TranslationResult("translated after retry", "fake")

    state = AppState()
    status = FakeStatus()
    overlay = FakeOverlay()
    translator = HangingThenWorkingTranslator()
    usecase = ReadTranslateUseCase(
        settings=AppSettings(saved_region=ScreenRegion(0, 0, 100, 50), request_timeout_seconds=0.01),
        state=state,
        region_selector=None,
        screenshot_service=FakeScreenshot(),
        translator=translator,
        overlay_window=overlay,
        status_window=status,
    )

    usecase.run()
    assert translator.started.wait(timeout=5)
    assert state.snapshot().read == ReadState.ERROR
    assert "timed out" in status.messages[-1]

    usecase.run()

    assert state.snapshot().read == ReadState.OVERLAY_VISIBLE
    assert overlay.text == "translated after retry"

from __future__ import annotations

import threading

from PIL import Image

from snaptranslate.application.read_translate_usecase import ReadTranslateUseCase
from snaptranslate.domain.models import AppSettings, ScreenRegion, TranslationResult
from snaptranslate.domain.state import AppState


class FakeScreenshot:
    def capture(self, region: ScreenRegion) -> Image.Image:
        return Image.new("RGB", (region.width, region.height), "white")


class FakeOcr:
    def extract_text(self, image: Image.Image):
        from snaptranslate.domain.models import OcrResult

        return OcrResult("hello")


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
        def translate(self, text: str, prompt: str) -> TranslationResult:
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
        ocr_service=FakeOcr(),
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

    assert status.messages.count("[read]: translating") == 1
    assert "[read]: busy" in status.messages
    assert overlay.text == "translated"

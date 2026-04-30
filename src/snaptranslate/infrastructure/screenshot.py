from __future__ import annotations

from PIL import Image, ImageGrab

from snaptranslate.domain.models import ScreenRegion


class ScreenshotService:
    def capture(self, region: ScreenRegion) -> Image.Image:
        region.validate()
        return ImageGrab.grab(bbox=region.box)


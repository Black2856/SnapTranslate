from __future__ import annotations

import base64
from io import BytesIO
from typing import Protocol

from PIL import Image


class ImageEncoder(Protocol):
    def to_data_url(self, image: Image.Image) -> str:
        ...


class PngDataUrlEncoder:
    def to_data_url(self, image: Image.Image) -> str:
        buffer = BytesIO()
        image.save(buffer, format="PNG")
        encoded = base64.b64encode(buffer.getvalue()).decode("ascii")
        return f"data:image/png;base64,{encoded}"

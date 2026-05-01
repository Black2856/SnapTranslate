from __future__ import annotations

import base64

from PIL import Image

from snaptranslate.infrastructure.image_encoder import PngDataUrlEncoder


def test_png_data_url_encoder_outputs_png_data_url() -> None:
    image = Image.new("RGB", (2, 2), "white")

    data_url = PngDataUrlEncoder().to_data_url(image)

    prefix = "data:image/png;base64,"
    assert data_url.startswith(prefix)
    assert base64.b64decode(data_url[len(prefix) :]).startswith(b"\x89PNG")

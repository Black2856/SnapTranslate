from __future__ import annotations

from snaptranslate.domain.models import AppSettings


def test_old_read_translation_prompt_migrates_to_read_image_prompt() -> None:
    settings = AppSettings.from_json_dict(
        {
            "read_translation_prompt": "old prompt",
            "ocr_language": "en",
        }
    )

    assert settings.read_image_prompt == "old prompt"
    assert "ocr_language" not in settings.to_json_dict()

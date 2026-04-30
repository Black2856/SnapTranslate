from __future__ import annotations

import logging

from snaptranslate.infrastructure.paths import app_data_dir


def configure_logging() -> None:
    log_path = app_data_dir() / "snaptranslate.log"
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
        handlers=[
            logging.FileHandler(log_path, encoding="utf-8"),
            logging.StreamHandler(),
        ],
    )


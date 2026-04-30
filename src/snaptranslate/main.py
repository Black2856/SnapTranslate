from __future__ import annotations

from snaptranslate.app import SnapTranslateApp
from snaptranslate.infrastructure.logging import configure_logging


def main() -> int:
    configure_logging()
    app = SnapTranslateApp()
    app.start()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

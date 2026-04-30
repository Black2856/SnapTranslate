# Repository Guidelines

## Project Structure & Module Organization

Requirements and design notes live in `doc/requirements.md` and `doc/design.md`. Implementation lives under `src/snaptranslate/`.

Keep the root small and place application code under `src/snaptranslate/`. Follow the package split:

- `src/snaptranslate/domain/`: settings models, state, value objects.
- `src/snaptranslate/application/`: use cases and hotkey orchestration.
- `src/snaptranslate/infrastructure/`: OCR, ChatGPT API, clipboard, config, logging.
- `src/snaptranslate/presentation/`: pywin32 windows, overlay, input box, settings UI.
- `tests/unit/` and `tests/integration/`: automated tests.

## Build, Test, and Development Commands

This project should use `uv` for Python environment and dependency management.

- `uv sync`: install dependencies from `pyproject.toml` and `uv.lock`.
- `uv sync --extra ocr`: install PaddleOCR support.
- `uv run python -m snaptranslate`: run the app locally.
- `uv run pytest -p no:cacheprovider`: run the test suite.
- `uv run ruff check .`: run lint checks if Ruff is configured.
- `uv run ruff format .`: format Python files if Ruff formatting is configured.

Do not add ad hoc scripts to the repository root unless they are project entry points.

## Coding Style & Naming Conventions

Use Python 3 with type hints for public interfaces and cross-module boundaries. Prefer small classes with clear responsibilities over large procedural modules. Use 4-space indentation.

Naming:

- Modules and packages: `snake_case`
- Classes: `PascalCase`
- Functions, methods, variables: `snake_case`
- Constants: `UPPER_SNAKE_CASE`
- Tests: `test_<behavior>.py`

Keep Windows-specific pywin32 code isolated in `presentation/` or `infrastructure/`.

## Testing Guidelines

Use `pytest` for tests. Unit tests should cover settings validation, state transitions, hotkey parsing, translator error handling, and clipboard behavior. Integration tests should mock OCR and ChatGPT API calls rather than making live requests.

Avoid tests that require real global hotkeys, screen capture, or API credentials unless they are explicitly marked as manual or integration-only.

## Commit & Pull Request Guidelines

The current Git history only contains an initial commit, so no repository-specific convention is established yet. Use short imperative commit messages, for example:

- `Add OCR translation requirements`
- `Implement settings store`
- `Fix overlay visibility toggle`

Pull requests should include a concise summary, test results, linked issues when applicable, and screenshots or screen recordings for UI changes.

## Security & Configuration Tips

Never commit API keys, local config files, screenshots containing sensitive content, or logs with request payloads. Prefer `OPENAI_API_KEY` for ChatGPT API credentials. If local configuration is added, store it outside the repository or ensure it is ignored by Git.

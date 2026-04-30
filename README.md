# SnapTranslate

SnapTranslate is a Windows desktop tool for prompt-based translation.

It provides two workflows:

- OCR a selected screen region with PaddleOCR, translate it with the ChatGPT API, and show the result in a black overlay box.
- Open a hotkey-driven input box, translate the entered text, and copy the translated result to the clipboard.

## Setup

```powershell
uv sync
```

PaddleOCR is optional until OCR is used:

```powershell
uv sync --extra ocr
```

PaddlePaddle is not expected to work on every Python version. Use Python 3.11 or 3.12 for OCR:

```powershell
uv python pin 3.11
uv sync --extra ocr
```

If `.venv` was already created with Python 3.13, remove `.venv` and run the commands above again.

Set your API key before translating:

```powershell
$env:OPENAI_API_KEY = "..."
```

## Run

```powershell
uv run snaptranslate
```

Default hotkeys:

- `Ctrl+Shift+F8`: run OCR translation, or hide the overlay if visible.
- `Ctrl+Shift+F9`: show or hide the text input window.

Right-click the tray icon to open settings or quit.

## Settings

- `Read hotkey`: starts OCR translation. If the overlay is visible, the same hotkey hides it. Example: `Ctrl+Shift+F8`.
- `Input hotkey`: shows or hides the manual text input window. Example: `Ctrl+Shift+F9`.
- `ChatGPT model`: OpenAI model used for both OCR and manual text translation.
- `PaddleOCR language`: source language for OCR recognition, not the translation target. Use `japan` for Japanese, `en` for English, `ch` for Simplified Chinese, or `korean` for Korean.
- `Overlay text color`: text color on the read-translation overlay. Use a hex color such as `#FFFFFF`.
- `Overlay font`: font family for overlay text, for example `Yu Gothic UI`.
- `Overlay font size`: overlay text size in points.
- `Show status`: shows a small status indicator such as `[read]: translating` or `[input]: copied`.
- `Keep input draft on hide`: keeps text in the input window when it is hidden. Enter still hides the window after starting translation.
- `Enable local history JSONL`: writes translation history to `%APPDATA%/SnapTranslate/history.jsonl`.
- `Region mode`: `Saved` uses the registered screen rectangle; `Interactive drag each time` asks you to drag a region for every OCR run.
- `Set saved region`: lets you drag and save the OCR target area used by `Saved` mode.
- `Read translation prompt`: prompt template for OCR translation. Keep `{text}` where the OCR text should be inserted.
- `Input translation prompt`: prompt template for manual text translation. Keep `{text}` where the typed text should be inserted.

After saving settings, restart the app to re-register changed hotkeys.

## Development

```powershell
uv run pytest -p no:cacheprovider
uv run --extra dev ruff check .
```

The `-p no:cacheprovider` flag avoids pytest cache permission issues on this Windows environment.

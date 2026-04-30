# SnapTranslate

SnapTranslate is a Windows desktop tool for prompt-based translation.

It provides two workflows:

- OCR a selected screen region with PaddleOCR, translate it with the ChatGPT API, and show the result as a transparent overlay.
- Open a hotkey-driven input box, translate the entered text, and copy the translated result to the clipboard.

## Setup

```powershell
uv sync
```

PaddleOCR is optional until OCR is used:

```powershell
uv sync --extra ocr
```

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

## Development

```powershell
uv run pytest -p no:cacheprovider
uv run --extra dev ruff check .
```

The `-p no:cacheprovider` flag avoids pytest cache permission issues on this Windows environment.

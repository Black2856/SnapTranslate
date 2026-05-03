# SnapTranslate

SnapTranslate is a Windows desktop tool for prompt-based translation.

It provides two workflows:

- Send a selected screen region image to the ChatGPT API, translate the text found in the image, and show the result in an overlay.
- Open a hotkey-driven input box, translate the entered text, and copy the translated result to the clipboard.

## Setup

```powershell
uv sync
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

- `Ctrl+Shift+F8`: run image translation, or hide the overlay if visible.
- `Ctrl+Shift+F9`: show or hide the text input window.

Right-click the tray icon to open settings or quit.

## Settings

- `Read hotkey`: starts image translation. If the overlay is visible, the same hotkey hides it. Example: `Ctrl+Shift+F8`.
- `Input hotkey`: shows or hides the manual text input window. Example: `Ctrl+Shift+F9`.
- `ChatGPT model`: OpenAI model used for both image and manual text translation. The read workflow requires a model that supports image input.
- `Overlay text color`: text color on the read-translation overlay. Use a hex color such as `#FFFFFF`.
- `Overlay font`: font family for overlay text, for example `Yu Gothic UI`.
- `Overlay font size`: overlay text size in points.
- `Show status`: shows a small status indicator such as `[read]: translating` or `[input]: copied`.
- `Keep input draft on hide`: keeps text in the input window when it is hidden. Enter still hides the window after starting translation.
- `Enable local history JSONL`: writes translation history to `%APPDATA%/SnapTranslate/history.jsonl`.
- `Region mode`: `Saved` uses the registered screen rectangle; `Interactive drag each time` asks you to drag a region for every image translation run.
- `Set saved region`: lets you drag and save the image translation target area used by `Saved` mode.
- `Read image translation prompt`: prompt for reading and translating text from the captured image.
- `Input translation prompt`: prompt template for manual text translation. Keep `{text}` where the typed text should be inserted.

After saving settings, restart the app to re-register changed hotkeys.

## Development

```powershell
uv run pytest -p no:cacheprovider
uv run --extra dev ruff check .
```

The `-p no:cacheprovider` flag avoids pytest cache permission issues on this Windows environment.

## Deployment

SnapTranslate can be packaged as a Windows `onedir` executable. Stop any running SnapTranslate instance before building so `uv` can update the local environment.

```powershell
uv sync --extra dev
uv run pyinstaller --clean --noconfirm --distpath deploy/dist --workpath deploy/build deploy/packaging/snaptranslate.spec
```

The deployable app is created at:

```text
deploy/dist/SnapTranslate/SnapTranslate.exe
```

Distribute the whole `deploy/dist/SnapTranslate/` folder, not only `SnapTranslate.exe`, because `_internal/` contains the bundled runtime files. The recipient does not need Python, uv, or project dependencies installed.

Runtime settings and logs are stored under `%APPDATA%/SnapTranslate`. Do not embed API keys in the executable; set `OPENAI_API_KEY` on the target machine before running translations.

Generated files under `deploy/build/` and `deploy/dist/` are ignored by Git. See `deploy/packaging/README.md` for the focused packaging notes.

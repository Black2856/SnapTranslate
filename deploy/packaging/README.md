# Windows exe build

SnapTranslate can be packaged as a Windows `onedir` executable with PyInstaller.

## Build

```powershell
uv sync --extra dev
uv run pyinstaller --clean --noconfirm --distpath deploy/dist --workpath deploy/build deploy/packaging/snaptranslate.spec
```

The executable is created at:

```text
deploy/dist/SnapTranslate/SnapTranslate.exe
```

Distribute the whole `deploy/dist/SnapTranslate/` folder. The recipient does not need Python, uv, or the project dependencies installed.

## Configuration

Runtime settings are stored under `%APPDATA%/SnapTranslate`. Logs are written to `%APPDATA%/SnapTranslate/snaptranslate.log`.

Do not embed API keys in the executable. Set `OPENAI_API_KEY` on the target machine before running translations.

## Notes

This build uses PyInstaller `onedir` rather than `onefile` to keep startup faster and make missing-DLL issues easier to diagnose. The generated `deploy/build/` and `deploy/dist/` directories are ignored by Git.

# -*- mode: python ; coding: utf-8 -*-

from pathlib import Path


block_cipher = None
ROOT = Path(SPECPATH).parents[1]

hiddenimports = [
    "pywintypes",
    "pythoncom",
    "win32api",
    "win32clipboard",
    "win32con",
    "win32gui",
    "win32timezone",
]

a = Analysis(
    [str(ROOT / "src" / "snaptranslate" / "main.py")],
    pathex=[str(ROOT / "src")],
    binaries=[],
    datas=[(str(ROOT / "deploy" / "packaging" / "README_user.txt"), ".")],
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="SnapTranslate",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name="SnapTranslate",
)

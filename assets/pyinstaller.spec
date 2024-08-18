# -*- mode: python ; coding: utf-8 -*-

# Spec file for PyInstaller.
# This is executable Python code. PyInstaller builds the app by executing the contents of this file.
# https://pyinstaller.org/en/stable/spec-files.html

from pathlib import Path

PROJECT_ROOT = Path(SPECPATH).parent.resolve(strict=True)
BUILD_WORK_DIR = PROJECT_ROOT / 'build'
BUILD_WORK_APP_DIR = BUILD_WORK_DIR / 'app'


a = Analysis(
    [str(BUILD_WORK_APP_DIR / 'src/hd_active/main.py')],
    pathex=[],
    binaries=[],
    # https://pyinstaller.org/en/stable/spec-files.html#adding-data-files
    datas=[],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

# onefile
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='hd_active',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

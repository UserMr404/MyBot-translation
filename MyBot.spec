# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller spec file for MyBot.

Build with:
    pyinstaller MyBot.spec

Output: dist/MyBot.exe
"""

import os
import sys
from pathlib import Path

from PyInstaller.utils.hooks import collect_submodules

block_cipher = None

# Repository root (where this spec file lives)
ROOT = Path(SPECPATH)

# Ensure the repo root is on sys.path so PyInstaller can find the mybot package
sys.path.insert(0, str(ROOT))

# Data files to bundle (source, destination_in_bundle)
datas = [
    (str(ROOT / 'MyBot' / 'imgxml'), 'imgxml'),
    (str(ROOT / 'MyBot' / 'Languages'), 'Languages'),
    (str(ROOT / 'MyBot' / 'CSV'), 'CSV'),
    (str(ROOT / 'MyBot' / 'images'), 'images'),
    (str(ROOT / 'MyBot' / 'lib'), 'lib'),
]

# Filter out any data dirs that don't exist (optional components)
datas = [(src, dst) for src, dst in datas if os.path.exists(src)]

a = Analysis(
    [str(ROOT / 'mybot' / 'app.py')],
    pathex=[str(ROOT)],
    binaries=[],
    datas=datas,
    hiddenimports=[
        'PyQt6.QtWidgets',
        'PyQt6.QtCore',
        'PyQt6.QtGui',
        'cv2',
        'numpy',
        'psutil',
        'configparser',
    ] + collect_submodules('mybot'),
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'tkinter',
        'matplotlib',
        'scipy',
        'pandas',
        'IPython',
        'jupyter',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
    module_collection_mode={'mybot': 'py'},
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='MyBot',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,           # Windowed mode (no console)
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=str(ROOT / 'MyBot' / 'images' / 'MyBot.ico')
    if (ROOT / 'MyBot' / 'images' / 'MyBot.ico').exists()
    else None,
)

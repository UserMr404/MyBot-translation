# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller spec file for MyBot.

Build with:
    pyinstaller MyBot.spec

Output: dist/MyBot.exe
"""

import os
import sys
from pathlib import Path

from PyInstaller.utils.hooks import collect_all, collect_submodules

block_cipher = None

# Repository root (where this spec file lives)
ROOT = Path(SPECPATH)

# Ensure the repo root is on sys.path so PyInstaller can find the mybot package
sys.path.insert(0, str(ROOT))

# Collect the mybot package (submodules, data files, binaries)
mybot_datas, mybot_binaries, mybot_hiddenimports = collect_all('mybot')

# Fallback: if collect_all found no submodules (package not pip-installed),
# discover them manually from the source tree.
if not mybot_hiddenimports:
    import pkgutil
    import importlib
    try:
        import mybot as _pkg
        mybot_hiddenimports = [
            name for _imp, name, _ispkg
            in pkgutil.walk_packages(_pkg.__path__, prefix='mybot.')
        ]
    except ImportError:
        # Last resort: scan .py files on disk
        mybot_hiddenimports = []
        _mybot_dir = ROOT / 'mybot'
        for _py in _mybot_dir.rglob('*.py'):
            _rel = _py.relative_to(ROOT)
            _mod = str(_rel.with_suffix('')).replace(os.sep, '.')
            if _mod != 'mybot.__main__':
                mybot_hiddenimports.append(_mod)
    mybot_hiddenimports.append('mybot')

# Data files to bundle (source, destination_in_bundle)
datas = [
    (str(ROOT / 'MyBot' / 'imgxml'), 'imgxml'),
    (str(ROOT / 'MyBot' / 'Languages'), 'Languages'),
    (str(ROOT / 'MyBot' / 'CSV'), 'CSV'),
    (str(ROOT / 'MyBot' / 'images'), 'images'),
    (str(ROOT / 'MyBot' / 'lib'), 'lib'),
] + mybot_datas

# Filter out any data dirs that don't exist (optional components)
datas = [(src, dst) for src, dst in datas if os.path.exists(src)]

a = Analysis(
    [str(ROOT / 'launcher.py')],
    pathex=[str(ROOT)],
    binaries=mybot_binaries,
    datas=datas,
    hiddenimports=[
        'PyQt6.QtWidgets',
        'PyQt6.QtCore',
        'PyQt6.QtGui',
        'cv2',
        'numpy',
        'psutil',
        'configparser',
    ] + mybot_hiddenimports,
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

# -*- mode: python ; coding: utf-8 -*-

# PyInstaller spec for the Pico desktop pet executable.
# This bundles the Qt backend (PyQt5 or PySide6) and the compiled resources.
# Run with: pyinstaller pico/desktop/pyinstaller_pet.spec

import os
from PyInstaller.utils.hooks import collect_submodules, copy_metadata
from PyInstaller.building.build_main import Analysis, PYZ, EXE, COLLECT

# Helper to include both PyQt5 and PySide6 modules (whichever is used).
qt_modules = []
try:
    import PyQt5
    qt_modules = collect_submodules('PyQt5')
except Exception:
    pass
try:
    import PySide6
    qt_modules += collect_submodules('PySide6')
except Exception:
    pass

# Include the pico package and its data files.
pathex = [os.path.abspath('.'),]

# Add the .qrc compiled resources (if you generate resources_rc.py).
# We'll also include the raw .qrc file so the executable can load it at runtime.

datas = [
    ('pico/desktop/resources.qrc', 'pico/desktop'),
]

# Hidden imports for Qt plugins (platforms, styles etc.)
hiddenimports = qt_modules

# Collect package metadata for proper licensing info.
hiddenimports += copy_metadata('pico')

# Build analysis.
a = Analysis(
    ['pico/desktop/pet_cli.py'],
    pathex=pathex,
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=None)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    name='pico-pet',
    debug=False,
    strip=False,
    upx=True,
    console=False,  # GUI app – no console window
    icon=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    name='pico-pet',
)

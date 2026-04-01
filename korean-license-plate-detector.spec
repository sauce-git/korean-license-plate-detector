# -*- mode: python ; coding: utf-8 -*-
# PyInstaller spec file for Korean License Plate Detector

import os
import sys
from pathlib import Path

block_cipher = None

# Detect platform for platform-specific settings
is_macos = sys.platform == 'darwin'
is_windows = sys.platform == 'win32'

# Use onefile for Windows, onedir for Linux/macOS
is_onefile = is_windows

# Get cache directory
cache_dir = os.environ.get('HF_MODEL_CACHE', '.cache')

# Data files to include from src/
datas = [
    ('src/klpd/ui/resources/form.ui', 'klpd/ui/resources'),
    ('src/klpd/ui/resources/icons/dobby.ico', 'klpd/ui/resources/icons'),
    ('src/klpd/utils/data/kor_list.txt', 'klpd/utils/data'),
    ('src/klpd/utils/data/plate_list.txt', 'klpd/utils/data'),
]

# Include cached models if they exist
models_dir = Path(cache_dir) / 'models'
if models_dir.exists():
    datas.append((str(models_dir), 'models'))

hiddenimports = [
    'onnxruntime',
    'cv2',
    'numpy',
    'PySide6.QtCore',
    'PySide6.QtGui',
    'PySide6.QtWidgets',
    'PySide6.QtUiTools',
    'openpyxl',
    'huggingface_hub',
    'huggingface_hub.file_download',
    'klpd',
    'klpd.detector',
    'klpd.models',
    'klpd.utils',
]

a = Analysis(
    ['src/klpd/cli.py'],
    pathex=['src/'],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'torch', 'torchvision', 'ultralytics',
        'tensorflow', 'keras', 'matplotlib', 'pandas', 'seaborn',
        'scipy', 'PIL', 'IPython', 'jupyter',
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
    a.binaries if is_onefile else [],
    a.zipfiles if is_onefile else [],
    a.datas if is_onefile else [],
    [],
    exclude_binaries=not is_onefile,
    name='korean-license-plate-detector',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,  # Disable UPX to avoid code signing issues
    console=False,  # GUI app, logs go to file
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,  # No code signing during build
    entitlements_file=None,
)

# Only create COLLECT for onedir builds (not onefile)
if not is_onefile:
    coll = COLLECT(
        exe,
        a.binaries,
        a.zipfiles,
        a.datas,
        strip=False,
        upx=True,
        upx_exclude=[],
        name='korean-license-plate-detector',
    )

# -*- mode: python ; coding: utf-8 -*-
# PyInstaller spec file for Korean License Plate Detector

import os
import sys
from pathlib import Path

block_cipher = None

# Detect platform for platform-specific settings
is_macos = sys.platform == 'darwin'
is_windows = sys.platform == 'win32'

# Get cache directory
cache_dir = os.environ.get('HF_MODEL_CACHE', '.cache')

# Data files to include from src/
datas = [
    ('src/form.ui', '.'),
    ('src/utils/data', 'utils/data'),
    ('src/utils/icons', 'utils/icons'),
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
]

a = Analysis(
    ['src/widget.py'],
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
    [],
    exclude_binaries=True,
    name='korean-license-plate-detector',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,  # GUI app, logs go to file
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity='-' if is_macos else None,  # Ad-hoc signing for macOS
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
    name='korean-license-plate-detector',
)

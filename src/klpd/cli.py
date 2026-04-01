# -*- coding: utf-8 -*-
"""CLI entry point for Korean License Plate Detector"""

import sys
import os

# Set environment variables before importing klpd modules
HF_MODEL_REPO = os.environ.get('HF_MODEL_REPO', 'sauce-hug/korean-license-plate-detector')
HF_MODEL_CACHE = os.environ.get('HF_MODEL_CACHE', '.cache')


def main():
    """Main entry point for CLI"""
    from klpd.ui.main_window import main as ui_main
    ui_main()


if __name__ == '__main__':
    main()

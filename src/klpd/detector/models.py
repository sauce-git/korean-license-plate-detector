# -*- coding: utf-8 -*-
# Model instances and initialization

from klpd.utils import debug_print, info_print
from klpd.models import load_model, DetectPlate, WarpPlate, DetectNumber

# Model names
PLATE_DETECT_MODEL = "plate_detect_v1"
VERTEX_DETECT_MODEL = "vertex_detect_v1"
SYLLABLE_DETECT_MODEL = "syllable_detect_v1"

# Global model instances (lazy loaded)
_plate_detector = None
_vertex_detector = None
_syllable_detector = None


def _load_models():
    """Load all detection models (lazy initialization)"""
    global _plate_detector, _vertex_detector, _syllable_detector

    if _plate_detector is not None:
        return  # Already loaded

    debug_print("Loading models...")
    info_print("Loading detection models...")

    _plate_detector = DetectPlate(load_model(PLATE_DETECT_MODEL))
    debug_print(f"plate_detector loaded: {_plate_detector}")

    _vertex_detector = WarpPlate(load_model(VERTEX_DETECT_MODEL))
    debug_print(f"vertex_detector loaded: {_vertex_detector}")

    _syllable_detector = DetectNumber(load_model(SYLLABLE_DETECT_MODEL))
    debug_print(f"syllable_detector loaded: {_syllable_detector}")

    debug_print("All models loaded!")
    info_print("Detection models loaded successfully")


def get_plate_detector():
    """Get plate detector instance (lazy loaded)"""
    _load_models()
    return _plate_detector


def get_vertex_detector():
    """Get vertex detector instance (lazy loaded)"""
    _load_models()
    return _vertex_detector


def get_syllable_detector():
    """Get syllable detector instance (lazy loaded)"""
    _load_models()
    return _syllable_detector

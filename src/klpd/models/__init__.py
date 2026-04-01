# -*- coding: utf-8 -*-
"""Model loading and management"""

from .loader import (
    load_model,
    get_model_path,
    download_model_from_hf,
    download_all_models,
    MODEL_NAMES,
)
from .plate import DetectPlate, crop_img
from .vertex import WarpPlate, warp
from .number import DetectNumber, sort_num, nms

__all__ = [
    # loader
    "load_model",
    "get_model_path",
    "download_model_from_hf",
    "download_all_models",
    "MODEL_NAMES",
    # plate
    "DetectPlate",
    "crop_img",
    # vertex
    "WarpPlate",
    "warp",
    # number
    "DetectNumber",
    "sort_num",
    "nms",
]

# ONNX model loader with Hugging Face Hub support

import os
import sys
import cv2
import numpy as np
import onnxruntime as ort
import logging
from pathlib import Path

# Limit threading to avoid issues with QThread in PyInstaller
os.environ['OMP_NUM_THREADS'] = '1'
os.environ['MKL_NUM_THREADS'] = '1'
os.environ['OPENBLAS_NUM_THREADS'] = '1'
os.environ['VECLIB_MAXIMUM_THREADS'] = '1'
os.environ['NUMEXPR_NUM_THREADS'] = '1'

# Setup logging - always set to INFO level to allow logs to propagate
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Debug mode and debug_print from common module
from klpd.utils import debug_print, is_debug_enabled, info_print

if is_debug_enabled():
    logger.debug("DEBUG mode enabled")

# Configuration from environment variables
HF_MODEL_REPO = os.environ.get('HF_MODEL_REPO', 'sauce-hug/korean-license-plate-detector')
HF_MODEL_CACHE = os.environ.get('HF_MODEL_CACHE', '.cache')

logger.debug(f"HF_MODEL_REPO: {HF_MODEL_REPO}")
logger.debug(f"HF_MODEL_CACHE: {HF_MODEL_CACHE}")

MODEL_NAMES = ['plate_detect_v1', 'vertex_detect_v1', 'syllable_detect_v1']


def get_cache_dir() -> Path:
    """Get cache directory for models"""
    return Path(HF_MODEL_CACHE)


def download_model_from_hf(model_name: str, cache_dir: Path) -> Path:
    """Download model from Hugging Face Hub"""
    from huggingface_hub import hf_hub_download

    model_filename = f"{model_name}/weights/best.onnx"
    local_dir = cache_dir / 'models'

    model_path = hf_hub_download(
        repo_id=HF_MODEL_REPO,
        filename=model_filename,
        local_dir=local_dir,
        local_dir_use_symlinks=False  # Ensure actual files, not symlinks
    )
    return Path(model_path)


def get_model_path(model_name: str) -> Path:
    """Get model path, checking bundled models first, then cache, then download"""
    # Check bundled models (PyInstaller)
    if getattr(sys, 'frozen', False):
        bundled_model = Path(sys._MEIPASS) / 'models' / model_name / 'weights' / 'best.onnx'
        logger.info(f"Checking bundled model: {bundled_model}")
        logger.info(f"Exists: {bundled_model.exists()}")
        if bundled_model.exists():
            logger.info(f"Using bundled model: {model_name}")
            return bundled_model
        else:
            logger.warning("Bundled model not found, will try cache/download")

    # Check cache
    cache_dir = get_cache_dir()
    cached_model = cache_dir / 'models' / model_name / 'weights' / 'best.onnx'
    logger.info(f"Checking cache: {cached_model}")
    if cached_model.exists():
        logger.info(f"Using cached model: {model_name}")
        return cached_model

    # Download from Hugging Face
    logger.info(f"Downloading {model_name} from {HF_MODEL_REPO}...")
    return download_model_from_hf(model_name, cache_dir)


class ONNXModel:
    """ONNX model wrapper with YOLO-compatible output format"""

    def __init__(self, model_path):
        self.model_path = str(model_path)
        logger.info(f"Loading ONNX model from: {self.model_path}")
        try:
            # Set single-threaded execution to avoid issues with QThread in PyInstaller
            so = ort.SessionOptions()
            so.intra_op_num_threads = 1
            so.inter_op_num_threads = 1
            so.execution_mode = ort.ExecutionMode.ORT_SEQUENTIAL

            self.session = ort.InferenceSession(
                self.model_path,
                providers=['CPUExecutionProvider'],
                sess_options=so
            )
            self.input_name = self.session.get_inputs()[0].name
            self.input_shape = self.session.get_inputs()[0].shape
            self.input_size = self.input_shape[2] if len(self.input_shape) == 4 else 416
            logger.info(f"Model loaded: {self.input_name}, shape: {self.input_shape}")
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            raise

    def preprocess(self, img):
        h, w = img.shape[:2]
        scale = min(self.input_size / h, self.input_size / w)
        new_h, new_w = int(h * scale), int(w * scale)

        img_resized = cv2.resize(img, (new_w, new_h))

        pad_h = (self.input_size - new_h) // 2
        pad_w = (self.input_size - new_w) // 2

        img_padded = np.full((self.input_size, self.input_size, 3), 114, dtype=np.uint8)
        img_padded[pad_h:pad_h + new_h, pad_w:pad_w + new_w] = img_resized

        img_rgb = cv2.cvtColor(img_padded, cv2.COLOR_BGR2RGB)
        img_normalized = img_rgb.astype(np.float32) / 255.0
        img_chw = np.transpose(img_normalized, (2, 0, 1))
        img_batch = np.expand_dims(img_chw, 0)

        return img_batch, scale, pad_h, pad_w

    def postprocess(self, outputs, orig_shape, scale, pad_h, pad_w, conf_threshold=0.25):
        predictions = outputs[0]
        debug_print(f"Raw output shape: {predictions.shape}")

        if predictions.shape[1] < predictions.shape[2]:
            predictions = np.transpose(predictions, (0, 2, 1))
            debug_print(f"Transposed to: {predictions.shape}")

        return YOLOResult(predictions, orig_shape, scale, pad_h, pad_w, conf_threshold)

    def __call__(self, img):
        orig_shape = img.shape[:2]
        debug_print(f"Inference on image shape: {orig_shape}")
        input_tensor, scale, pad_h, pad_w = self.preprocess(img)
        outputs = self.session.run(None, {self.input_name: input_tensor})
        return [self.postprocess(outputs, orig_shape, scale, pad_h, pad_w)]


class YOLOResult:
    def __init__(self, predictions, orig_shape, scale, pad_h, pad_w, conf_threshold=0.25):
        self.predictions = predictions[0]
        self.orig_shape = orig_shape
        self.scale = scale
        self.pad_h = pad_h
        self.pad_w = pad_w
        self.conf_threshold = conf_threshold
        self._boxes = None

    @property
    def boxes(self):
        if self._boxes is None:
            self._boxes = self._parse_boxes()
        return self._boxes

    def _parse_boxes(self):
        boxes_list = []
        debug_print(f"Parsing boxes from {len(self.predictions)} predictions")
        debug_print(f"Confidence threshold: {self.conf_threshold}")

        for i, pred in enumerate(self.predictions):
            if len(pred) < 5:
                continue

            x, y, w, h = pred[:4]
            class_scores = pred[4:]

            class_id = np.argmax(class_scores)
            confidence = class_scores[class_id]

            if confidence < self.conf_threshold:
                continue

            debug_print(f"Box {i}: cls={class_id}, conf={confidence:.3f}, xywh=({x:.1f}, {y:.1f}, {w:.1f}, {h:.1f})")

            x1 = (x - w / 2 - self.pad_w) / self.scale
            y1 = (y - h / 2 - self.pad_h) / self.scale
            x2 = (x + w / 2 - self.pad_w) / self.scale
            y2 = (y + h / 2 - self.pad_h) / self.scale

            x1 = max(0, min(x1, self.orig_shape[1]))
            y1 = max(0, min(y1, self.orig_shape[0]))
            x2 = max(0, min(x2, self.orig_shape[1]))
            y2 = max(0, min(y2, self.orig_shape[0]))

            boxes_list.append(YOLOBox(x1, y1, x2, y2, w, h, class_id, confidence))

        debug_print(f"Total boxes found: {len(boxes_list)}")

        return YOLOBoxes(boxes_list)


class YOLOBoxes:
    def __init__(self, boxes):
        self._boxes = boxes

    def __len__(self):
        return len(self._boxes)

    def __iter__(self):
        return iter(self._boxes)

    def __getitem__(self, idx):
        return self._boxes[idx]

    @property
    def xyxy(self):
        if len(self._boxes) == 0:
            return np.array([])
        return np.array([b._xyxy for b in self._boxes])

    @property
    def xywh(self):
        if len(self._boxes) == 0:
            return np.array([])
        return np.array([b._xywh for b in self._boxes])

    @property
    def xywhn(self):
        return self.xywh

    @property
    def cls(self):
        if len(self._boxes) == 0:
            return np.array([])
        return np.array([b.cls for b in self._boxes])

    def tolist(self):
        return self.xyxy.tolist()


class YOLOBox:
    def __init__(self, x1, y1, x2, y2, w, h, cls, conf):
        self._xyxy = np.array([x1, y1, x2, y2])
        self._xywh = np.array([(x1 + x2) / 2, (y1 + y2) / 2, w, h])
        self._cls = int(cls)
        self._conf = conf

    @property
    def xyxy(self):
        return ArrayWrapper([self._xyxy])

    @property
    def xywh(self):
        return ArrayWrapper([self._xywh])

    @property
    def cls(self):
        return self._cls

    @property
    def conf(self):
        return self._conf

    def center_x(self):
        """Get center x coordinate directly (for PyInstaller compatibility)"""
        return float(self._xywh[0])

    def center_y(self):
        """Get center y coordinate directly (for PyInstaller compatibility)"""
        return float(self._xywh[1])


class ArrayWrapper:
    def __init__(self, data):
        self._data = np.array(data)

    def tolist(self):
        return self._data.tolist()

    def __array__(self):
        return self._data

    def __getitem__(self, idx):
        return self._data[idx]


def load_model(model_name):
    """Load ONNX model"""
    model_path = get_model_path(model_name)
    return ONNXModel(model_path)


def download_all_models():
    """Download all models from Hugging Face"""
    logger.info(f"Downloading models from {HF_MODEL_REPO}...")
    for model_name in MODEL_NAMES:
        try:
            path = get_model_path(model_name)
            logger.info(f"  [OK] {model_name}")
        except Exception as e:
            logger.error(f"  [FAIL] {model_name}: {e}")
    logger.info("Done!")

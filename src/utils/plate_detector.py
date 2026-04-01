# This file contains the class for detecting and cropping the license plate from the image

from utils.debug import debug_print


def crop_img(img, result):
    """Crop license plate from image using detection result"""
    boxes = result[0].boxes

    if len(boxes) == 0:
        debug_print("No boxes detected")
        return None

    # If multiple boxes, select the one with highest confidence
    if len(boxes) > 1:
        debug_print(f"Multiple boxes detected ({len(boxes)}), selecting highest confidence")
        best_idx = 0
        best_conf = 0
        for i, box in enumerate(boxes):
            conf = box.conf if hasattr(box, 'conf') else 0
            if conf > best_conf:
                best_conf = conf
                best_idx = i
        box = boxes[best_idx]
    else:
        box = boxes[0]

    # Get coordinates
    coords = box.xyxy.tolist()[0]
    x1, y1, x2, y2 = coords
    debug_print(f"Cropping box: x1={x1:.1f}, y1={y1:.1f}, x2={x2:.1f}, y2={y2:.1f}")

    # Crop image
    cropped_img = img[int(y1):int(y2), int(x1):int(x2)]
    debug_print(f"Cropped image shape: {cropped_img.shape}")

    return cropped_img


class DetectPlate:
    """Class for detecting and cropping license plate from image"""

    def __init__(self, model):
        self.model = model

    def detect_and_crop(self, img):
        """Detect license plate and return cropped image"""
        result = self.model(img)
        cropped_img = crop_img(img, result)
        return cropped_img

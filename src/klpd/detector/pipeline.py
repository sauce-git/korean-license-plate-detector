# -*- coding: utf-8 -*-
# License plate detection pipeline

import re
import cv2
import numpy as np
from .models import get_plate_detector, get_vertex_detector, get_syllable_detector
from klpd.utils import debug_print, info_print

# Regex patterns
PLATE_REGEX = r'([가-힣]{2}[0-9]{2}[가-힣]{1}[0-9]{4})|([0-9]{2,3}[가-힣]{1}[0-9]{4})'
OUTPUT_REGEX = r'([0-9]{2,3}[가-힣]{1}[0-9]{4})'


def confirm_num(plate_num1, plate_num2, mask=True):
    """
    Confirm and return the license plate number.

    Args:
        plate_num1: First OCR result
        plate_num2: Second OCR result
        mask: If True, apply output regex mask

    Returns:
        Confirmed plate number or None
    """
    if plate_num1 is None:
        plate_num1 = ''
    if plate_num2 is None:
        plate_num2 = ''

    m1 = re.fullmatch(PLATE_REGEX, plate_num1)
    m2 = re.fullmatch(PLATE_REGEX, plate_num2)

    if plate_num1 == plate_num2 and m1 is not None:
        plate_num = plate_num1
    else:
        if m1 is not None:
            plate_num = plate_num1
        elif m2 is not None:
            plate_num = plate_num2
        else:
            return None

    if mask:
        plate_num = re.search(OUTPUT_REGEX, plate_num).group()

    return plate_num


def get_num(img, save=False, save_not_detected=False, save_path='./temp_data/',
            save_name='temp'):
    """
    Detect and return the license plate number from an image.

    Args:
        img: Input image (numpy array)
        save: Whether to save all intermediate images
        save_not_detected: Whether to save image when detection fails
        save_path: Directory to save images
        save_name: Base name for saved images

    Returns:
        Detected license plate number or None
    """
    debug_print(f"get_num called with image shape: {img.shape if img is not None else None}")

    # Input validation
    if img is None:
        debug_print("Image is None, returning None")
        return None
    if not isinstance(img, np.ndarray) or img.size == 0:
        debug_print("Image is empty or invalid, returning None")
        return None

    # Normalize save path
    if not save_path.endswith('/'):
        save_path += '/'
    if save_name.endswith('/'):
        save_name = save_name[:-1]

    # Get model instances
    plate_detector = get_plate_detector()
    vertex_detector = get_vertex_detector()
    syllable_detector = get_syllable_detector()

    # Step 1: Detect and crop license plate
    debug_print("Running plate detection...")
    cropped_img = plate_detector.detect_and_crop(img)
    debug_print(f"cropped_img: {cropped_img.shape if cropped_img is not None else None}")

    # Step 2: Detect vertices and warp
    if cropped_img is not None:
        debug_print("Running vertex detection and warp...")
        warped_img = vertex_detector.detect_and_warp(cropped_img)
        debug_print(f"warped_img: {warped_img.shape if warped_img is not None else None}")
    else:
        warped_img = None

    # Step 3: OCR on cropped image
    if cropped_img is not None:
        debug_print("Running OCR on cropped image...")
        res1 = syllable_detector.get_num_from_img(cropped_img)
        debug_print(f"res1 (cropped): {res1}")
    else:
        res1 = None
        debug_print("No cropped image, res1 = None")

    # Step 4: OCR on warped image
    if warped_img is not None:
        debug_print("Running OCR on warped image...")
        res2 = syllable_detector.get_num_from_img(warped_img)
        debug_print(f"res2 (warped): {res2}")
    else:
        res2 = None
        debug_print("No warped image, res2 = None")

    # Step 5: Confirm result
    result = confirm_num(res1, res2, mask=False)
    debug_print(f"Final result: {result}")
    if result:
        info_print(f"License plate detected: {result}")

    # Step 6: Save images if requested
    if save:
        cv2.imwrite(f"{save_path}origin_{save_name}.jpg", img)
        if cropped_img is not None:
            cv2.imwrite(f"{save_path}cropped_{save_name}.jpg", cropped_img)
        if warped_img is not None:
            cv2.imwrite(f"{save_path}warped_{save_name}.jpg", warped_img)

    elif result is None and save_not_detected:
        if warped_img is not None:
            cv2.imwrite(f"{save_path}{save_name}.jpg", warped_img)
        elif cropped_img is not None:
            cv2.imwrite(f"{save_path}{save_name}.jpg", cropped_img)
        else:
            cv2.imwrite(f"{save_path}{save_name}.jpg", img)

    return result

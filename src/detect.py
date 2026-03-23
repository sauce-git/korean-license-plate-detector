# This file contains the class for detecting and cropping the license plate from the image

import re
import cv2
import os
import sys

# Debug mode
DEBUG = os.environ.get('DEBUG', '').lower() in ('1', 'true', 'yes')

def debug_print(*args, **kwargs):
    if DEBUG:
        print("[DEBUG]", *args, **kwargs, file=sys.stderr, flush=True)

from utils.model_loader import load_model
from utils.plate_detector import DetectPlate
from utils.plate_warper import WarpPlate
from utils.number_detector import DetectNumber

regex = '([가-힣]{2}[0-9]{2}[가-힣]{1}[0-9]{4})|([0-9]{2,3}[가-힣]{1}[0-9]{4})'  # regex for license plate number
output_regex = '([0-9]{2,3}[가-힣]{1}[0-9]{4})'  # regex for wanted license plate number

# set the model names
plate_detect_model = "plate_detect_v1"
vertex_detect_model = "vertex_detect_v1"
syllable_detect_model = "syllable_detect_v1"

debug_print("Loading models...")

# load the models
plate_detector = DetectPlate(load_model(plate_detect_model))
debug_print(f"plate_detector loaded: {plate_detector}")

vertex_detector = WarpPlate(load_model(vertex_detect_model))
debug_print(f"vertex_detector loaded: {vertex_detector}")

syllable_detector = DetectNumber(load_model(syllable_detect_model))
debug_print(f"syllable_detector loaded: {syllable_detector}")

debug_print("All models loaded!")


def get_num(img, save=False, save_not_detected=False, save_path='./temp_data/',
            save_name='temp'):  # return the license plate number
    debug_print(f"get_num called with image shape: {img.shape if img is not None else None}")

    if save_path[-1] != '/':  # add '/' to the end of the path if it doesn't exist
        save_path += '/'
    if save_name[-1] == '/':  # remove '/' from the end of the name if it exists
        save_name = save_name[:-1]

    debug_print("Running plate detection...")
    cropped_img = plate_detector.detect_and_crop(img)  # crop the image
    debug_print(f"cropped_img: {cropped_img.shape if cropped_img is not None else None}")

    if cropped_img is not None:
        debug_print("Running vertex detection and warp...")
        warped_img = vertex_detector.detect_and_warp(cropped_img)  # warp the image
        debug_print(f"warped_img: {warped_img.shape if warped_img is not None else None}")
    else:
        warped_img = None

    if cropped_img is not None:
        debug_print("Running OCR on cropped image...")
        res1 = syllable_detector.get_num_from_img(cropped_img)  # get the number from the cropped image
        debug_print(f"res1 (cropped): {res1}")
    else:
        res1 = None
        debug_print("No cropped image, res1 = None")

    if warped_img is not None:
        debug_print("Running OCR on warped image...")
        res2 = syllable_detector.get_num_from_img(warped_img)  # get the number from the warped image
        debug_print(f"res2 (warped): {res2}")
    else:
        res2 = None
        debug_print("No warped image, res2 = None")

    result = confirm_num(res1, res2)  # return the number that is confirmed to be the license plate number
    debug_print(f"Final result: {result}")

    if save:
        cv2.imwrite(save_path + "origin_" + save_name + ".jpg", img)
        cv2.imwrite(save_path + "cropped_" + save_name + ".jpg", cropped_img)
        cv2.imwrite(save_path + "warped_" + save_name + ".jpg", warped_img)

    elif result is None and save_not_detected:
        if warped_img is not None:
            cv2.imwrite(save_path + save_name + ".jpg", warped_img)
        elif cropped_img is not None:
            cv2.imwrite(save_path + save_name + ".jpg", cropped_img)
        else:
            cv2.imwrite(save_path + save_name + ".jpg", img)

    return result


def confirm_num(plate_num1, plate_num2, mask=True):  # return the confirmed license plate number
    if plate_num1 is None:
        plate_num1 = ''
    if plate_num2 is None:
        plate_num2 = ''

    m1 = re.fullmatch(regex, plate_num1)
    m2 = re.fullmatch(regex, plate_num2)

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
        plate_num = re.search(output_regex, plate_num).group()

    return plate_num

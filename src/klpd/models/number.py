# This module is for detecting number in the image and returning the ordered number

import numpy as np
from klpd.utils.data_loader import load_kor_list
from klpd.utils import debug_print

kor_list = load_kor_list()


def nms(boxes, iou_threshold=0.5):
    """Non-Maximum Suppression to remove overlapping boxes"""
    if len(boxes) == 0:
        return []

    # Get box data
    boxes_data = []
    for i, box in enumerate(boxes):
        xyxy = box.xyxy.tolist()[0]
        conf = box.conf if hasattr(box, 'conf') else 1.0
        boxes_data.append({
            'idx': i,
            'x1': xyxy[0],
            'y1': xyxy[1],
            'x2': xyxy[2],
            'y2': xyxy[3],
            'conf': conf,
            'cls': box.cls
        })

    # Sort by confidence
    boxes_data.sort(key=lambda x: x['conf'], reverse=True)

    keep = []
    while len(boxes_data) > 0:
        best = boxes_data.pop(0)
        keep.append(best['idx'])

        remaining = []
        for box in boxes_data:
            # Calculate IoU
            x1 = max(best['x1'], box['x1'])
            y1 = max(best['y1'], box['y1'])
            x2 = min(best['x2'], box['x2'])
            y2 = min(best['y2'], box['y2'])

            inter_area = max(0, x2 - x1) * max(0, y2 - y1)
            box1_area = (best['x2'] - best['x1']) * (best['y2'] - best['y1'])
            box2_area = (box['x2'] - box['x1']) * (box['y2'] - box['y1'])
            union_area = box1_area + box2_area - inter_area

            iou = inter_area / union_area if union_area > 0 else 0

            if iou < iou_threshold:
                remaining.append(box)

        boxes_data = remaining

    return keep


def get_linear(x1, y1, x2, y2):
    if (x2 - x1) == 0:
        return 1, 0
    a = (y2 - y1) / (x2 - x1)
    b = y1 - a * x1
    return a, b


def is_on_line(box, line):
    x1, y1, x2, y2 = box.xyxy.tolist()[0]
    x = (x1 + x2) / 2
    line_y = line[0] * x + line[1]

    if line_y < y1 or line_y > y2:
        return False
    return True


def sort_num(boxes):
    if len(boxes.xywhn.tolist()) == 0:
        return None

    # Apply NMS first
    debug_print(f"About to call NMS with {len(boxes)} boxes")
    keep_indices = nms(list(boxes), iou_threshold=0.3)
    debug_print(f"NMS: {len(boxes)} boxes -> {len(keep_indices)} boxes")

    if len(keep_indices) == 0:
        debug_print("No boxes after NMS, returning None")
        return None

    # Filter boxes - this is where it might freeze in PyInstaller
    debug_print(f"About to filter boxes, keep_indices: {keep_indices[:3]}...")
    filtered_boxes = [boxes[i] for i in keep_indices]
    debug_print(f"Filtered boxes count: {len(filtered_boxes)}")

    # Get min/max by x position
    x_positions = [b.center_x() for b in filtered_boxes]
    max_idx = x_positions.index(max(x_positions))
    min_idx = x_positions.index(min(x_positions))

    max_box = filtered_boxes[max_idx]
    min_box = filtered_boxes[min_idx]

    x1, y1 = max_box.xywh.tolist()[0][:2]
    x2, y2 = min_box.xywh.tolist()[0][:2]

    line = get_linear(x1, y1, x2, y2)
    debug_print(f"Line equation: y={x1}x+{y1}")

    box_on_line = []
    rest = []

    for box in filtered_boxes:
        if is_on_line(box, line):
            box_on_line.append(box)
        else:
            rest.append(box)

    debug_print(f"Boxes on line: {len(box_on_line)}, Rest: {len(rest)}")

    debug_print("About to sort box_on_line...")
    try:
        box_on_line.sort(key=lambda x: x.center_x())
        debug_print("box_on_line sorted")
    except Exception as e:
        debug_print(f"Error sorting box_on_line: {e}")
        raise

    debug_print("About to sort rest...")
    try:
        rest.sort(key=lambda x: x.center_x())
        debug_print("rest sorted")
    except Exception as e:
        debug_print(f"Error sorting rest: {e}")
        raise

    plate_num = ''

    debug_print(f"Processing {len(rest)} rest boxes...")
    for i, box in enumerate(rest):
        cls_val = int(box.cls)
        debug_print(f"Rest box {i}: cls={cls_val}")
        if 0 <= cls_val < len(kor_list):
            plate_num += kor_list[cls_val]

    debug_print(f"Processing {len(box_on_line)} boxes on line...")
    for i, box in enumerate(box_on_line):
        cls_val = int(box.cls)
        debug_print(f"Box on line {i}: cls={cls_val}")
        if 0 <= cls_val < len(kor_list):
            plate_num += kor_list[cls_val]

    debug_print(f"Detected plate number (before formatting): {plate_num}")

    # Handle Korean region names
    if plate_num and plate_num[0] > '9':
        region_set = ['서울', '경기', '부산', '강원', '충남', '충북', '전남', '전북', '경남', '경북', '제주']
        region = plate_num[:2]
        if region not in region_set:
            plate_num = plate_num[1] + plate_num[0] + plate_num[2:]

        region = plate_num[:2]
        if region not in region_set:
            plate_num = plate_num[2:]

    return plate_num


def max_min_idx(boxes):
    # Use center_x() for PyInstaller compatibility
    boxes_x = [b.center_x() for b in boxes]
    boxes_rank = boxes_x.copy()
    boxes_rank.sort()
    max_idx = boxes_x.index(boxes_rank[-1])
    min_idx = boxes_x.index(boxes_rank[0])
    return max_idx, min_idx


class DetectNumber:
    def __init__(self, model):
        self.model = model

    def get_num_from_img(self, img):
        result = self.model(img)
        boxes = result[0].boxes
        plate_num = sort_num(boxes)
        return plate_num

# This module is for detecting number in the image and returning the ordered number

import numpy as np
from utils.data_loader import load_kor_list
from utils.debug import debug_print

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
    keep_indices = nms(list(boxes), iou_threshold=0.3)
    debug_print(f"NMS: {len(boxes)} boxes -> {len(keep_indices)} boxes")

    if len(keep_indices) == 0:
        return None

    # Filter boxes
    filtered_boxes = [boxes[i] for i in keep_indices]

    # Get min/max by x position
    x_positions = [b.xywh.tolist()[0][0] for b in filtered_boxes]
    max_idx = x_positions.index(max(x_positions))
    min_idx = x_positions.index(min(x_positions))

    max_box = filtered_boxes[max_idx]
    min_box = filtered_boxes[min_idx]

    x1, y1 = max_box.xywh.tolist()[0][:2]
    x2, y2 = min_box.xywh.tolist()[0][:2]

    line = get_linear(x1, y1, x2, y2)

    box_on_line = []
    rest = []

    for box in filtered_boxes:
        if is_on_line(box, line):
            box_on_line.append(box)
        else:
            rest.append(box)

    box_on_line.sort(key=lambda x: x.xywh[0][0])
    rest.sort(key=lambda x: x.xywh[0][0])

    plate_num = ''

    for box in rest:
        plate_num += kor_list[int(box.cls)]

    for box in box_on_line:
        plate_num += kor_list[int(box.cls)]

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
    boxes_x = list(list(zip(*boxes.xywhn.tolist()))[0])
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

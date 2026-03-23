from glob import glob
import os
import mat73
# This code is for converting mat file into txt file

import cv2

BASE_DIR = os.getcwd()

def parse_str(str):
    return int(str.split('(')[1].split('.')[0])


def get_yolo_bbox(x, y, width, height, img_shape):
    print(x, y, width, height, img_shape)

    x_center = (x + width / 2) / img_shape[1]
    y_center = (y + height / 2) / img_shape[0]
    width = width / img_shape[1]
    height = height / img_shape[0]
    return [x_center, y_center, width, height]


def modify(mat_bboxes, img_list):
    for img_path in img_list:
        img_name = img_path.split('\\')[-1].split('.')[0]
        img = cv2.imread(img_path)
        print(img_name)

        mat_bbox = mat_bboxes[int(img_name)-1]

        yolo_line = ''

        if(type(mat_bbox['label']) == list):
            for idx in range(len(mat_bbox['label'])):
                bbox = get_yolo_bbox(mat_bbox['left'][idx], mat_bbox['top'][idx], mat_bbox['width'][idx], mat_bbox['height'][idx], img.shape)

                label = int(mat_bbox['label'][idx])
                if label == 10:
                    label = 0

                yolo_line += str(label) + ' ' + ' '.join(map(str, bbox))
                if(idx < len(mat_bbox['label'])-1):
                    yolo_line += '\n'
        else:
            label = int(mat_bbox['label'])
            if label == 10:
                label = 0

            bbox = get_yolo_bbox(mat_bbox['left'], mat_bbox['top'], mat_bbox['width'], mat_bbox['height'], img.shape)
            yolo_line += str(label) + ' ' + ' '.join(map(str, bbox))

        with open('labels/' + img_name + '.txt', 'w') as f:
            f.write(yolo_line)



os.chdir(BASE_DIR+"/content/number")

mat_bboxes = mat73.loadmat('digitStruct.mat')['digitStruct']['bbox']

img_list = glob("images/*.png")

modify(mat_bboxes, img_list)
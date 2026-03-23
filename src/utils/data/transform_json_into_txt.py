# This code is for converting json file into txt file

import json
import os
import shutil
from glob import glob

default_rect = " 0.5 0.5 1 1"

kor_list = [
    '0', '1', '2', '3', '4', '5', '6', '7', '8', '9',
    '가', '나', '다', '라', '마', '아', '자', '하',
    '거', '너', '더', '러', '머', '버', '서', '어', '저', '허',
    '고', '노', '도', '로', '모', '보', '소', '오', '조', '호',
    '구', '누', '두', '루', '무', '부', '수', '우', '주',
    '배',
    '외', '교', '임', '울', '산', '대', '구', '인', '천', '광', '전', '경', '기', '강', '원', '충', '북', '남', '전', '제', '세',
    '바', '사', '차', '카', '타',' 파'
]

BASE_DIR = os.getcwd()

def modify(json_data, img_list, start_idx=0):
    classes = open('labels/classes.txt', 'w')

    for i in range(len(kor_list)):
        classes.write(kor_list[i]+'\n')

    for img_path in img_list:
        img_name = img_path.split('\\')[-1].split('.')[0]
        print(img_name)

        text = json_data[int(img_name)-start_idx]['text']

        if text not in kor_list:
            continue

        yolo_line = str(kor_list.index(text)) + default_rect

        shutil.copy(img_path, 'images/' + img_name + '.png')
        with open('labels/' + img_name + '.txt', 'w') as f:
            f.write(yolo_line)

    classes.close()
    print("done!")

###augmented data###
"""
os.chdir(BASE_DIR+"/content/augmented")
print(os.getcwd())

img_list = glob('origin/*.png')
with open('augmentation_data_info.json', 'r', encoding='UTF8') as f:
    json_data = json.load(f)['annotations']

modify(json_data, img_list, 558600)
"""
###syllable data###
os.chdir(BASE_DIR+"/content/syllable")

img_list = glob('origin/*.png')
with open('printed_data_info.json', 'r', encoding='UTF8') as f:
    json_data = json.load(f)['annotations']

modify(json_data, img_list)
# Description: Load data from txt file

import os
import sys


def get_resource_path(relative_path):
    """Get path to resource, works in dev and PyInstaller bundle"""
    if getattr(sys, 'frozen', False):
        return os.path.join(sys._MEIPASS, relative_path)
    # Resources are in the same directory as this module (klpd/utils/)
    return os.path.join(os.path.dirname(__file__), relative_path)


def get_data_from_txt(path):
    result = []
    with open(path, 'r', encoding='UTF8') as f:
        lines = f.readlines()
    for line in lines:
        line = line.strip()
        result.append(line)
    return result


def load_kor_list():
    path = get_resource_path('data/kor_list.txt')
    return get_data_from_txt(path)


def load_plate_list():
    path = get_resource_path('data/plate_list.txt')
    return get_data_from_txt(path)


def add_to_plate_list(plate_num):
    path = get_resource_path('data/plate_list.txt')
    with open(path, 'a', encoding='UTF8') as f:
        f.write(plate_num + '\n')

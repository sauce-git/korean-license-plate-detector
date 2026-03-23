# -*- coding: utf-8 -*-
# Main window module

import os
import sys
import argparse

# Parse debug argument FIRST before any other imports
parser = argparse.ArgumentParser(add_help=False)
parser.add_argument('--debug', action='store_true', help='Enable debug mode')
args, _ = parser.parse_known_args()

# Set debug environment variable BEFORE importing other modules
if args.debug:
    os.environ['DEBUG'] = '1'
    print("[DEBUG] Debug mode enabled", file=sys.stderr, flush=True)

from glob import glob
import cv2
from PySide6 import QtGui
from PySide6.QtCore import QFile, QIODevice, QThread, QEventLoop, Qt
from PySide6.QtGui import QPixmap
from PySide6.QtUiTools import QUiLoader
from PySide6.QtWidgets import QApplication, QFileDialog, QMainWindow
from openpyxl.workbook import Workbook

from detect import get_num

title = "Number Detector"


def get_resource_path(relative_path):
    """Get path to resource, works in dev and PyInstaller bundle"""
    if getattr(sys, 'frozen', False):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.dirname(__file__), relative_path)


def remake_dir_path(path):
    if path[-1] != '/':
        path += '/'
    return path


def save_result(result, save_path='temp_data/', save_name='result'):
    save_path = remake_dir_path(save_path)
    if not os.path.exists(save_path):
        os.makedirs(save_path)

    wb = Workbook()
    ws = wb.active

    for i in range(len(result)):
        ws.cell(row=i + 1, column=1, value=result[i])
        wb.save(save_path + save_name + ".xlsx")


class Worker(QThread):
    def __init__(self, convert_dir_to_num_list, img_list):
        super().__init__()
        self.convert_dir_to_num_list = convert_dir_to_num_list
        self.img_list = img_list

    def run(self):
        self.convert_dir_to_num_list(self.img_list)


class MainWindow(QMainWindow):
    def __init__(self, window):
        super().__init__()

        self.img_list = None
        self.result = []
        self.worker = None
        self.window = window

        self.dir = None
        self.file = None
        self.car_num = None

        self.window.chooseDir.clicked.connect(self.choose_dir)
        self.window.chooseFile.clicked.connect(self.choose_file)
        self.window.execute.clicked.connect(self.execute)
        self.window.confirm.clicked.connect(self.confirm)
        self.window.closeBtn.clicked.connect(self.close_app)
        self.local_event_loop = QEventLoop()

        window.setWindowTitle("")

        icon_path = get_resource_path('utils/icons/dobby.ico')
        app_icon = QtGui.QIcon(icon_path)
        window.setWindowIcon(app_icon)

        self.window.label.setText("경로를 선택해주세요")

    def choose_dir(self):
        dir = QFileDialog.getExistingDirectory(self.window, "Select Directory")

        self.img_list = glob(dir + "/*.jpeg")
        if len(self.img_list) == 0:
            self.img_list = glob(dir + "/*.jpg")
        if len(self.img_list) == 0:
            self.img_list = glob(dir + "/*.png")
        if len(self.img_list) == 0:
            self.window.label.setText("이미지 파일이 없습니다")
        else:
            self.window.label.setText("이미지 파일을 찾았습니다. 변환을 눌러주세요")
            self.set_image(self.img_list[0])

        self.file = ""
        self.dir = remake_dir_path(dir)
        self.window.progressBar.setValue(0)

    def choose_file(self):
        file = QFileDialog.getOpenFileName(self.window, "Select File")
        self.set_image(file[0])
        self.window.label.setText("이미지 파일을 찾았습니다(%s개). \n\n변환을 눌러주세요" % (len(self.img_list) if self.img_list else 1))
        self.dir = ""
        self.file = file[0]
        self.window.progressBar.setValue(0)

    def execute(self):
        self.window.label.setText("실행중입니다")

        if self.dir:
            self.worker = Worker(self.convert_dir_to_num_list, self.img_list)
            self.worker.finished.connect(self.on_worker_finished)
            self.worker.start()
            self.local_event_loop.exec()

            for idx in range(len(self.result)):
                if self.result[idx] is None:
                    self.set_image(self.img_list[idx])
                    self.window.label.setText("번호판을 인식하지 못했습니다. 번호판을 입력해주세요\n\n이미지: %s" % (self.img_list[idx]))
                    self.window.label.setWordWrap(True)
                    self.local_event_loop.exec()
                    self.result[idx] = self.car_num
                    self.car_num = None

            self.window.label.setText("처리중...")
            save_result(self.result, save_path=self.dir, save_name='result')
            self.window.label.setText("완료! 결과는 \n" + self.dir + "result.xlsx \n파일을 확인해주세요")

        elif self.file:
            img = cv2.imread(self.file)
            self.window.label.setText("완료!\n\n%s" % (get_num(img)))
            self.window.progressBar.setValue(100)

        else:
            self.window.label.setText("경로를 선택해주세요")

    def on_worker_finished(self):
        self.local_event_loop.exit()

    def confirm(self):
        self.car_num = self.window.car_num.text()
        self.window.car_num.setText("")
        self.window.label.setText(self.car_num)
        self.local_event_loop.exit()

    def close_app(self):
        QApplication.quit()

    def set_image(self, img):
        img_name = img.split('/')[-1]
        if os.path.isfile('temp_data/' + img_name):
            img = 'temp_data/' + img_name

        self.window.Image.setPixmap(QPixmap(img).scaled(
            self.window.Image.width(),
            self.window.Image.height(),
            Qt.KeepAspectRatio
        ))

    def convert_dir_to_num_list(self, img_list=None):
        result = []

        for img_path in img_list:
            print(img_path)
            img = cv2.imread(img_path)
            plate_num = get_num(img=img, save_not_detected=True, save_name=img_path)

            if plate_num is not None:
                result.append(plate_num)
            else:
                result.append(None)

            self.window.progressBar.setValue(int((img_list.index(img_path) + 1) / len(img_list) * 100))

        self.result = result


if __name__ == "__main__":
    app = QApplication(sys.argv)

    ui_file_path = get_resource_path("form.ui")
    ui_file = QFile(ui_file_path)

    if not ui_file.open(QIODevice.ReadOnly):
        print("Cannot open {}: {}".format(ui_file_path, ui_file.errorString()))
        sys.exit(-1)

    loader = QUiLoader()
    window = loader.load(ui_file)
    ui_file.close()

    if not window:
        print(loader.errorString())
        sys.exit(-1)

    main_window = MainWindow(window)
    window.show()

    sys.exit(app.exec())

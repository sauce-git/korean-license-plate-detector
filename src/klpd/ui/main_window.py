# -*- coding: utf-8 -*-
# Main window module

import os
import sys
import argparse
import logging
from pathlib import Path

# Setup logging - always log to file, console only in debug mode
log_dir = Path.home() / '.korean-license-plate-detector'
log_dir.mkdir(exist_ok=True)
log_file = log_dir / 'app.log'

# Ensure log file exists
if not log_file.exists():
    log_file.touch()

# Parse debug argument FIRST before any other imports
parser = argparse.ArgumentParser(add_help=False)
parser.add_argument('--debug', action='store_true', help='Enable debug mode')
args, _ = parser.parse_known_args()

# Set debug environment variable BEFORE importing other modules
if args.debug:
    os.environ['DEBUG'] = '1'

# Create formatters
file_formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s')
console_formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s')

# Create file handler - log INFO normally, DEBUG in debug mode
file_handler = logging.FileHandler(log_file, encoding='utf-8')
file_handler.setLevel(logging.DEBUG if args.debug else logging.INFO)
file_handler.setFormatter(file_formatter)

# Create console handler - use StreamHandler with level to control output
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.DEBUG if args.debug else logging.CRITICAL)
console_handler.setFormatter(console_formatter)

# Clear any existing handlers and configure root logger
for handler in logging.root.handlers[:]:
    logging.root.removeHandler(handler)

logging.root.setLevel(logging.DEBUG)  # Always allow DEBUG level
logging.root.addHandler(file_handler)
logging.root.addHandler(console_handler)

# Configure utils loggers to ensure propagation
utils_logger = logging.getLogger('utils')
utils_logger.setLevel(logging.DEBUG)
utils_logger.propagate = True

detector_logger = logging.getLogger('detector')
detector_logger.setLevel(logging.DEBUG)
detector_logger.propagate = True

# Log initialization message
logging.info("=" * 50)
logging.info("Application starting")
logging.info(f"Log file: {log_file}")
if args.debug:
    logging.info("Debug mode enabled")

from glob import glob
import cv2
from PySide6 import QtGui
from PySide6.QtCore import QFile, QIODevice, QThread, QEventLoop, Qt
from PySide6.QtGui import QPixmap
from PySide6.QtUiTools import QUiLoader
from PySide6.QtWidgets import QApplication, QFileDialog, QMainWindow
from PySide6.QtGui import QAction
from openpyxl.workbook import Workbook

from klpd.detector import get_num

title = "Number Detector"


def get_resource_path(relative_path):
    """Get path to resource, works in dev and PyInstaller bundle"""
    if getattr(sys, 'frozen', False):
        return os.path.join(sys._MEIPASS, relative_path)
    # Resources are in the 'resources' subdirectory
    return os.path.join(os.path.dirname(__file__), 'resources', relative_path)


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
        self.debug_mode = args.debug  # Store debug mode state

        self.dir = None
        self.file = None
        self.car_num = None

        self.window.chooseDir.clicked.connect(self.choose_dir)
        self.window.chooseFile.clicked.connect(self.choose_file)
        self.window.execute.clicked.connect(self.execute)
        self.window.confirm.clicked.connect(self.confirm)
        self.window.closeBtn.clicked.connect(self.close_app)
        self.local_event_loop = QEventLoop()

        # Set the loaded widget as the central widget of MainWindow
        self.setCentralWidget(window)

        window.setWindowTitle("")

        icon_path = get_resource_path('utils/icons/dobby.ico')
        app_icon = QtGui.QIcon(icon_path)
        self.setWindowIcon(app_icon)

        # Set window size and make it fixed
        self.resize(800, 600)
        self.setFixedSize(800, 600)

        # Add menu bar to MainWindow (not to the widget)
        self.create_menu_bar()

        # Show log file location for debugging
        self.update_status_message()

    def create_menu_bar(self):
        """Create menu bar with settings"""
        menu_bar = self.menuBar()

        # Settings menu
        settings_menu = menu_bar.addMenu("설정(Settings)")

        # Debug mode toggle
        self.debug_action = QAction("디버그 모드(Debug Mode)", self)
        self.debug_action.setCheckable(True)
        self.debug_action.setChecked(self.debug_mode)
        self.debug_action.triggered.connect(self.toggle_debug_mode)
        settings_menu.addAction(self.debug_action)

        # View log file
        view_log_action = QAction("로그 보기(View Log)", self)
        view_log_action.triggered.connect(self.view_log_file)
        settings_menu.addAction(view_log_action)

        # Open log folder
        open_log_folder_action = QAction("로그 폴더 열기(Open Log Folder)", self)
        open_log_folder_action.triggered.connect(self.open_log_folder)
        settings_menu.addAction(open_log_folder_action)

    def toggle_debug_mode(self, checked):
        """Toggle debug mode"""
        self.debug_mode = checked

        # Update debug state using the Debug singleton
        from klpd.utils import debug
        debug.enabled = checked

        # Update logging level for both file and console handlers
        file_level = logging.DEBUG if checked else logging.INFO
        console_level = logging.DEBUG if checked else logging.CRITICAL

        for handler in logging.root.handlers:
            if isinstance(handler, logging.FileHandler):
                handler.setLevel(file_level)
            elif isinstance(handler, logging.StreamHandler) and handler.stream == sys.stdout:
                handler.setLevel(console_level)

        if checked:
            logging.info("Debug mode enabled")
        else:
            logging.info("Debug mode disabled")

        self.update_status_message()

    def view_log_file(self):
        """Open log file with default text editor"""
        import subprocess
        import platform
        try:
            if platform.system() == 'Windows':
                os.startfile(str(log_file))
            elif platform.system() == 'Darwin':  # macOS
                subprocess.run(['open', str(log_file)])
            else:  # Linux
                subprocess.run(['xdg-open', str(log_file)])
        except Exception as e:
            self.window.label.setText(f"로그 파일 열기 실패:\n{log_file}\n\n에러: {e}")

    def open_log_folder(self):
        """Open the folder containing log files"""
        import subprocess
        import platform
        try:
            if platform.system() == 'Windows':
                subprocess.run(['explorer', str(log_dir)])
            elif platform.system() == 'Darwin':  # macOS
                subprocess.run(['open', str(log_dir)])
            else:  # Linux
                subprocess.run(['xdg-open', str(log_dir)])
        except Exception as e:
            self.window.label.setText(f"로그 폴더 열기 실패:\n{log_dir}\n\n에러: {e}")

    def update_status_message(self):
        """Update status message based on debug mode"""
        if self.debug_mode:
            self.window.label.setText(f"DEBUG MODE\n\n로그 파일: {log_file}\n\n경로를 선택해주세요")
        else:
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


def main():
    """Main entry point for the UI"""
    # Setup error logging for frozen executables
    import traceback
    if getattr(sys, 'frozen', False):
        log_path = os.path.join(os.path.expanduser('~'), 'korean-license-plate-detector-error.log')
        original_excepthook = sys.excepthook
        def custom_excepthook(exc_type, exc_value, exc_traceback):
            with open(log_path, 'w') as f:
                f.write(''.join(traceback.format_exception(exc_type, exc_value, exc_traceback)))
            original_excepthook(exc_type, exc_value, exc_traceback)
        sys.excepthook = custom_excepthook

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
    main_window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()

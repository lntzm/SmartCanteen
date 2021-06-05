import sys
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from Ui_Main_window2 import Ui_MainWindow2
from multiprocessing import Queue as ProcQueue

from database import Database
from user import User
from PlateProcess import RecgProcess, CapProcess

import time
import cv2


class Main_app(QMainWindow, Ui_MainWindow):

    def __init__(self):
        super().__init__()

        self.dish_disp_timer = QTimer() # 菜品显示 定时器
        self.user = User()

        self.set_ui()  # 初始化窗口UI
        self.db = Database("mongodb://localhost:27017/", "SmartCanteen")  # 初始化数据库
        self.init_dish()    # 初始化菜品识别（进程 + 线程）

    def set_ui(self):
        self.setupUi(self)
        self.ui_disp_logo()
        self.plate_disp_label.setScaledContents(True)

    """前端启动"""

    def start(self):
        self.start_dish()
        self.show()

    def start_dish(self):
        pass


    def init_dish(self):
        pass


    def disp_dish_video(self, dish_video_img):
        self.plate_disp_label.setPixmap(QPixmap.fromImage(dish_video_img))

    # 前端显示用户id
    def disp_user_id(self):
        user_id = self.face_search_proc.user_id_buffer.get()
        self.user_id_label.setText(user_id)
        self.welcome_label.setText("Welcome！")

    # 前端显示logo
    def ui_disp_logo(self):
        logo = cv2.imread("./first/logo.png")
        logo = cv2.resize(logo, (160, 120))
        logo = cv2.cvtColor(logo, cv2.COLOR_BGR2RGB)
        logo = QImage(logo.data, logo.shape[1], logo.shape[0], QImage.Format_RGB888)
        self.logo_label.setScaledContents(True)
        self.logo_label.setPixmap(QPixmap.fromImage(logo))

    """前端关闭 事件处理"""

    def closeEvent(self, event):
        # 关闭前端窗口
        event.accept()


if __name__ == "__main__":
    """前端主程序创建"""
    app = QApplication(sys.argv)
    main = Main_app()

    """启动"""
    main.start()

    """退出"""
    sys.exit(app.exec_())

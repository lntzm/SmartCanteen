import sys
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from Ui_Main_window import Ui_MainWindow
from multiprocessing import Queue as ProcQueue

#from database import Database
from user import User
from Face_search_proc import Face_search

import time
import numpy as np
import cv2

class Main_app(QMainWindow, Ui_MainWindow):

    def __init__(self):
        super().__init__()
        self.user_flag_queue = ProcQueue(1)        # 人脸识别成功标志
        self.dish_flag_queue = ProcQueue(1)        # 菜品识别完毕标志
        self.over_flag_queue = ProcQueue(1)        # 用户结算完毕标志
        self.face_disp_timer = QTimer()            # 人脸显示 定时器
        self.user = User()

        self.set_ui()           # 初始化窗口UI
        self.db = Database("mongodb://localhost:27017/", "SmartCanteen")    # 初始化数据库
        self.init_face()        # 初始化人脸（进程 + 线程）

        """测试按钮 以后删除"""
        self.btn_dish_over.clicked.connect(self.dish_test_signal)
        self.btn_bill_over.clicked.connect(self.bill_test_signal)
        
    def set_ui(self):
        self.setupUi(self)
        self.face_disp_label.setScaledContents(True)

    """前端启动"""
    def start(self):       
        self.start_face()
        self.show()

    def start_face(self):
        self.face_search_proc.start()
        self.face_thread.start()

    def init_face(self):

        # 创建人脸子进程
        self.face_search_proc = Face_search()
        self.face_img_buffer = self.face_search_proc.image_buffer
        self.face_search_proc.bind_flag(self.dish_flag_queue, self.user_flag_queue)

        # 创建人脸显示子线程 并绑定信号
        self.face_thread = Accept_face_thread(self.db,
                                              self.user,
                                              self.face_img_buffer, 
                                              self.user_flag_queue,
                                              self.over_flag_queue, 
                                              self.face_disp_timer,)
        
        self.face_thread.disp_face_signal.connect(self.disp_face_video)
        self.face_disp_timer.timeout.connect(self.face_thread.send_disp_signal)
        self.face_thread.timer_start_signal.connect(self.face_disp_timer.start)
        self.face_thread.disp_user_id_signal.connect(self.disp_user_id)

    # 前端显示人脸
    def disp_face_video(self, face_video_img):
        self.face_disp_label.setPixmap(QPixmap.fromImage(face_video_img))
    
    # 前端显示用户id
    def disp_user_id(self):
        user_id = self.face_search_proc.user_id_buffer.get()
        self.user_id_label.setText(user_id)
        self.welcome_label.setText("Welcome！")

    """前端关闭 事件处理"""
    def closeEvent(self, event):
        # 关闭人脸显示线程
        self.face_thread.stop()
        
        # 关闭人脸检测进程
        self.face_search_proc.stop()
        time.sleep(1)
        self.face_search_proc.terminate()
        self.face_search_proc.join()

        # 关闭前端窗口
        event.accept()

    """菜品准备完成  测试按钮"""
    def dish_test_signal(self):
        if self.dish_flag_queue.empty():
            self.dish_flag_queue.put((False, True))
            print("dish over signal send -> ")

    def bill_test_signal(self):
        if self.over_flag_queue.full():
            _ = self.over_flag_queue.get()
            self.face_thread.condition_lock.wakeAll()

"""接受人脸显示线程"""
class Accept_face_thread(QThread):

    disp_face_signal = pyqtSignal(QImage)
    timer_start_signal = pyqtSignal(int)
    disp_user_id_signal = pyqtSignal()

    def __init__(self, 
                 db,
                 user,
                 image_buffer, 
                 user_flag_queue,
                 over_flag_queue,
                 disp_timer):

        super().__init__()
        self.image_buffer = image_buffer
        self.user_flag_queue = user_flag_queue
        self.over_flag_queue = over_flag_queue
        self.disp_timer = disp_timer
        self.user = user
        self.db = db
        self.mutex = QMutex()
        self.condition_lock = QWaitCondition() 

    def stop(self):
        self.disp_timer.stop()
        self.terminate()

    def send_disp_signal(self):
        self.disp_face_signal.emit(self.img_disp)   # 发射显示人脸图像的信号

    def run(self):
        img = self.image_buffer.get()

        while True:
            # 如果人脸识别到用户 获得id
            if self.user_flag_queue.full():
                _ = self.user_flag_queue.get()
                self.disp_user_id_signal.emit() 
              
                # 替换的用户的图片
                img = cv2.imread("./UI_project/girl.png")
                img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

                """数据库读写"""
                # self.user.saveInfo(self.db)
                # self.user.pay(self.db)

                # self.db.commitRecord()
                # self.db.pushRecord()
                # self.db.cleanRecord()

                # 替换为用户图片 并将线程挂起 等待唤醒
                self.over_flag_queue.put(True)
                self.img_disp = QImage(img.data, img.shape[1], img.shape[0], QImage.Format_RGB888)
                self.disp_face_signal.emit(self.img_disp)
            
                self.condition_lock.wait(self.mutex)
            else:
                if not self.image_buffer.empty():
                    img = self.image_buffer.get()

            # 前端显示
            self.img_disp = QImage(img.data, img.shape[1], img.shape[0], QImage.Format_RGB888)
            # 前端显示计时器启动信号 每10ms发送一次显示的图片
            if self.disp_timer.isActive() == False:
                self.timer_start_signal.emit(10)

"""接受菜品识别线程"""
class Accept_dish_thread(QThread):
    def __init__(self, over_flag_queue, dish_flag_queue):
        super().__init__()
        self.over_flag_queue = over_flag_queue
        self.dish_flag_queue = dish_flag_queue
        
if __name__ == "__main__":

    """前端主程序创建"""
    app = QApplication(sys.argv)
    main = Main_app()

    """启动"""
    main.start()

    """退出"""
    sys.exit(app.exec_())
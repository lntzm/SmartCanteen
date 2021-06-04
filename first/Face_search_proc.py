from multiprocessing import Process, Manager
from multiprocessing import Queue as ProcQueue
from threading import Thread, Lock, Event
from queue import Queue
from user import User
import time
import cv2

from Camera_capture import Capture_thread


class Face_search(Process):
    def __init__(self,
                 device_id=0,
                 resolution=(480, 360),
                 cap_freq=1,
                 search_freq=5):
        super().__init__()
        self.image_buffer = ProcQueue(16)  # 人脸前端显示缓存（跨进程）
        self.user_id_buffer = ProcQueue(1)  # 用户id缓存（跨进程）
        self.device_id = device_id
        self.cap_freq = cap_freq
        self.search_freq = search_freq  # 人脸搜索频率
        self.resolution = resolution  # 前端显示分辨率
        self.frame_count = 0
        self.user_id = None
        self.stop_flag = Manager().list([False])  # 进程停止标志 使用多进程列表实现

    """给进程绑定标志"""

    def bind_flag(self, dish_flag_queue: ProcQueue, user_flag_queue: ProcQueue):
        self.dish_flag_queue = dish_flag_queue
        self.user_flag_queue = user_flag_queue

    def stop(self):
        # 跨进程通信
        self.stop_flag[0] = True

    def run(self):
        self.cap_lock = Lock()  # 相机缓存锁
        self.user_img_lock = Lock()  # 用户人脸搜索用相片缓存锁

        self.user_img_buffer = Queue(3)  # 用户人脸搜索用相片缓存
        self.id_buffer = Queue(1)  # 用户id缓存

        self.cap_thread = Capture_thread(self.cap_lock, self.device_id, self.cap_freq)
        self.cap_thread.setDaemon(True)  # 设置为守护线程
        self.user_id_thread = User_id_thread(self.user_img_buffer, self.id_buffer, self.user_img_lock)
        self.user_id_thread.setDaemon(True)
        self.cap_buffer = self.cap_thread.cap_buffer

        if self.cap_thread.connect_camera():  # 如果相机连接成功 则启动
            # 启动线程
            self.cap_thread.start()
            self.user_id_thread.start()
            self.frame = self.cap_buffer.get()

        while True:
            # 进程结束
            if self.stop_flag[0]:
                # 进程结束前 先关闭相机
                self.cap_thread.stop()
                break

            if self.dish_flag_queue.empty():
                # 显示人脸部分摄像头画面
                self.disp_face()
                continue

            # 如果菜品识别完毕 则开始人脸检测
            dish_over = self.dish_flag_queue.get()
            print("dish over signal received")
            if dish_over:
                self.face_search()

    # 人脸检测部分实现
    def face_search(self):
        # 唤醒百度API线程
        self.user_id_thread.wakeup()

        while True:
            if self.stop_flag[0]:
                break

            self.disp_face()

            if self.frame_count % self.search_freq == 0:

                with self.user_img_lock:
                    if self.user_img_buffer.full():
                        _ = self.user_img_buffer.get()
                    self.user_img_buffer.put(self.frame)
                self.frame_count = 0

            if self.id_buffer.full():
                self.user_id = self.id_buffer.get()
                self.user_id_buffer.put(self.user_id)
                self.user_flag_queue.put(True)
                break

            # if self.user_id is None:
            #     continue
            # else:
            #     self.user_id_buffer.put(self.user_id)
            #     self.user_flag_queue.put(True)
            #     break

    # 显示人脸摄像头部分
    def disp_face(self):
        with self.cap_lock:
            if not self.cap_buffer.empty():
                self.frame = self.cap_buffer.get()
            self.frame_count += 1

        if self.image_buffer.full():
            _ = self.image_buffer.get()

        img = cv2.resize(self.frame, self.resolution)  # 调整图像大小                
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        if not self.image_buffer.full():
            self.image_buffer.put(img)

        # 调用百度API部分


class User_id_thread(Thread):
    def __init__(self, image_buffer, id_buffer, img_lock, search_interval=0.1):
        super().__init__()
        self.img_buffer = image_buffer
        self.id_buffer = id_buffer
        self.img_lock = img_lock
        self.search_interval = search_interval
        self.user = User()
        self.block_event = Event()
        self.user_id = None

    def block(self):
        self.block_event.wait()
        self.block_event.clear()

    def wakeup(self):
        self.block_event.set()

    def run(self):
        img = self.img_buffer.get()
        while True:
            if not self.img_buffer.empty():
                with self.img_lock:
                    img = self.img_buffer.get()
            time.sleep(self.search_interval)
            if self.user.getID(img):
                self.id_buffer.put(self.user.id)
                # 识别到用户id后 线程挂起
                self.block()

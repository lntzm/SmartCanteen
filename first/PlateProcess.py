from multiprocessing import Process, Manager
from multiprocessing import Queue as ProcQueue
from threading import Thread, Lock, Event
from queue import Queue
from ImageHandle import *
from first.plate import Plate

from Camera_capture import Capture_thread
from baiduAPI import BaiduAPI
from database import Database


class PlateRecognize(Process):
    def __init__(self,
                 device_id,
                 db: Database,
                 plate_flag_queue: ProcQueue,
                 start_flag_queue: ProcQueue,
                 search_freq=30):
        super().__init__()
        self.image_buffer = ProcQueue(16)
        self.device_id = device_id
        self.search_freq = search_freq
        self.stop_flag = Manager().list([False])  # 进程停止标志 使用多进程列表实现
        self.frame_count = 0
        self.recognized_buffer = ProcQueue(1)
        self.db = db
        self.baiduAPI = BaiduAPI()

        # plate进程应该绑定的标志是start_flag_queue和plate_flag_queue
        # 当start_flag_queue不为空时，get这个queue，使之为空开始进行菜品识别
        # 菜品识别完成后，向空的plate_flag_queue中put进一个True
        self.plate_flag_queue = plate_flag_queue
        self.start_flag_queue = start_flag_queue

    def run(self):
        self.cap_lock = Lock()
        self.plate_img_lock = Lock()
        self.plate_img_buffer = Queue(6)

        self.cap_thread = Capture_thread(self.cap_lock, self.device_id, cap_freq=1)
        self.cap_thread.setDaemon(True)
        self.plate_recg_thread = PlateRecgThread(self.plate_img_buffer,
                                                 self.plate_img_lock,
                                                 self.recognized_buffer,
                                                 self.db,
                                                 self.baiduAPI)
        self.plate_recg_thread.setDaemon(True)
        self.cap_buffer = self.cap_thread.cap_buffer

        if self.cap_thread.connect_camera():
            # 启动盘子摄像头线程

            self.cap_thread.start()
            self.frame = self.cap_buffer.get()

        while True:
            if self.stop_flag[0]:
                self.cap_thread.stop()
                break

            if self.start_flag_queue.empty():
                self.disp_plate()
                continue

            if self.start_flag_queue.get():
                print("> 接收到餐盘识别启动")
                self.recognize_plate()

    def stop(self):
        self.stop_flag[0] = True

    def recognize_plate(self):
        # 唤醒识别线程
        self.plate_recg_thread.wakeup()

        while True:
            if self.stop_flag[0]:
                break

            self.disp_plate()

            if self.frame_count % self.search_freq == 0:

                with self.plate_img_lock:
                    if self.plate_img_buffer.full():
                        _ = self.plate_img_buffer.get()
                    self.plate_img_buffer.put(self.frame)
                self.frame_count = 0

            if self.recognized_buffer.full():
                _ = self.recognized_buffer.get()
                self.plate_flag_queue.put(True)
                break

    # 显示餐盘摄像头部分
    def disp_plate(self):
        with self.cap_lock:
            if not self.cap_buffer.empty():
                self.frame = self.cap_buffer.get()
            self.frame_count += 1

        if self.image_buffer.full():
            _ = self.image_buffer.get()

        # img = cv2.resize(self.frame, self.resolution)  # 调整图像大小
        img = cv2.cvtColor(self.frame, cv2.COLOR_BGR2RGB)
        if not self.image_buffer.full():
            self.image_buffer.put(img)


class PlateRecgThread(Thread):
    def __init__(self, image_buffer, img_lock, recognized_buffer, db, baiduAPI):
        super().__init__()
        self.img_buffer = image_buffer
        self.img_lock = img_lock
        self.block_event = Event()
        self.baiduAPI = baiduAPI
        self.db = db
        self.recognized_buffer = recognized_buffer

    def block(self):
        self.block_event.wait()
        self.block_event.clear()

    def wakeup(self):
        self.block_event.set()

    def run(self):
        print(self.img_buffer.qsize())
        frame = self.img_buffer.get()
        while True:
            if not self.img_buffer.empty():
                with self.img_lock:
                    frame = self.img_buffer.get()
            # time_start = time.time()
            images, img_marked = splitImg(frame)
            # time_end = time.time()
            # print('分割图片用时', time_end - time_start, 's')

            if not images:
                print("> 未发现餐盘")
                return
            # cv2.imwrite("img_marked.jpg", img_marked)
            print(f"> 发现了{len(images)}个餐盘")

            # 返回各分割图片识别结果
            for image in images:
                plate = Plate()
                image_b64 = CVEncodeb64(image)
                # time_start = time.time()
                print("> 开始检测餐盘id")
                id_found = plate.getID(self.baiduAPI, image_b64)
                if not id_found:
                    print("  > 未发现餐盘id")
                    return
                print(f"  > 餐盘id: {plate.id}")
                # time_end = time.time()
                # print('ID识别用时', time_end - time_start, 's')
                if self.db.findRecord(plate.id):
                    print(f"> 该餐盘({plate.id})已经成功识别并记录")
                    continue

                if self.db.findNoEatenPlate(plate.id):
                    print(f"> 餐盘({plate.id})已属于其他用户，请拿走餐盘")
                    return

                # time_start = time.time()
                print("> 开始进行菜品识别")
                name_found = plate.getName(self.baiduAPI, image_b64)
                if not name_found:
                    print("  > 菜品识别失败")
                    return  # 检测到了餐盘id但是识别不出菜品
                print(f"  > 菜名:{plate.name}")
                # time_end = time.time()
                # print('菜品识别用时', time_end - time_start, 's')

                plate.searchDB(self.db)
                # 保存到本地数据库
                plate.saveInfo(self.db)

            # for循环中所有图片的id和name都识别到了
            self.recognized_buffer.put(True)
            self.block()

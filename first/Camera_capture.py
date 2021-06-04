import cv2
from threading import Thread, Lock, Event
from queue import Queue

class Capture_thread(Thread):
    def __init__(self, lock, device_id=0, cap_freq=5):
        super().__init__()
        self.device_id = device_id
        self.cap = cv2.VideoCapture()
        self.cap_buffer = Queue(8)  # 相机图片缓存
        self.cap_freq = cap_freq  # 相机缓存写入频率
        self.lock = lock        # 相机缓存锁

    def connect_camera(self):
        # 如果是Linux 则不需要cv2.CAP_DSHOW
        self.cap.open(self.device_id, cv2.CAP_DSHOW)

        if not self.cap.isOpened():
            print("Cannot open camera {}".format(self.device_id))
            return False
        else:
            return True

    def disconnect_camera(self):
        if self.cap.isOpened():
            self.cap.release()

    def stop(self):
        self.disconnect_camera()
        print("camera released")

    def run(self):
        frame_count = 0
        while True:   
            _, frame = self.cap.read()
            if not _ :
                continue
            frame_count += 1
            
            if frame_count == self.cap_freq:
                with self.lock:
                    if self.cap_buffer.full():
                        _ = self.cap_buffer.get()
                    self.cap_buffer.put(frame)
                frame_count = 0
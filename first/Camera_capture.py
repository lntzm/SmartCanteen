import cv2
from threading import Thread, Lock, Event
from queue import Queue


class Capture_thread(Thread):
    def __init__(self, device_id=0):
        super().__init__()
        self.device_id = device_id
        self.cap = cv2.VideoCapture()
        self.cap_buffer = Queue(32)  # 相机图片缓存

    def connect_camera(self):
        # 如果是Linux 则不需要cv2.CAP_DSHOW
        self.cap.open(self.device_id)

        if not self.cap.isOpened():
            print("Cannot open camera {}".format(self.device_id))
            return False
        else:
            print(f"camera {self.device_id} start")
            return True

    def disconnect_camera(self):
        if self.cap.isOpened():
            self.cap.release()

    def stop(self):
        self.disconnect_camera()
        print("camera released")

    def run(self):
        while True:
            _, frame = self.cap.read()
            if not _:
                continue

            if self.cap_buffer.full():
                _ = self.cap_buffer.get()
            self.cap_buffer.put(frame)

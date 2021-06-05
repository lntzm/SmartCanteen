from multiprocessing import Process, Queue
from second.hx711 import HX711
from second.plate import Plate
from ImageHandle import *

import numpy as np
import cv2


class RecgProcess(Process):
    def __init__(self, db, baiduAPI, img_queue: Queue):
        super().__init__()
        hx1 = HX711(dout_pin=21, pd_sck_pin=20, offset=68753, ratio=433.21)
        hx2 = HX711(dout_pin=26, pd_sck_pin=19, offset=-1660, ratio=430.05)
        hx3 = HX711(dout_pin=6, pd_sck_pin=5, offset=177856, ratio=424.71)
        self.hxs = [hx1, hx2, hx3]
        self.plates = [Plate(), Plate(), Plate()]
        self.got_weight = np.array([False, False, False])
        self.max_num_plates = len(self.hxs)
        self.db = db
        self.baiduAPI = baiduAPI
        self.img_queue = img_queue
        self.start_enable = False
        self.end_flag = False

    def run(self) -> None:
        while True:
            frame = self.img_queue.get()
            if self.end_flag:  # 完成了识别，需要拿走所有餐盘
                if self.checkAnyWeight():  # 还有重量，continue
                    continue
                else:  # 全部拿走了，开始下一轮识别
                    self.end_flag = False

            self.start_enable = self.checkAnyWeight()  # 新一轮，检测到重量开始识别
            if not self.start_enable:
                continue

            for hx, plate in zip(self.hxs, self.plates):
                plate.getWeight(hx)
            self.got_weight = (np.array([
                plate.rest_weight for plate in self.plates]) > 0)
            if np.all(self.got_weight == False):  # 全都未检测到重量
                print("> 压力传感器未检测到餐盘")
                continue

            images, locs = splitImg(frame)
            if not images:
                print("> 未检测到餐盘图像")
                continue
            if len(images) != np.count_nonzero(self.got_weight):
                print(f"> 压力传感器检测餐盘个数({np.count_nonzero(self.got_weight)})"
                      f"与餐盘图像个数({len(images)})不符")
                continue

            sync_imgs = sortImgByHX711(images, locs, self.got_weight)
            print(f"压力传感器与摄像头均发现了{len(images)}个餐盘")

            for i in range(self.max_num_plates):
                if not self.got_weight[i]:
                    continue
                plate = self.plates[i]
                img_b64 = CVEncodeb64(sync_imgs[i])
                print("> 开始识别餐盘id")
                id_found = self.plates[i].getID(self.baiduAPI, img_b64)
                if not id_found:
                    print("  > 未发现餐盘id")
                    break
                print(f"  > 餐盘id: {plate.id}")

                info_found = plate.getInfoBefore(self.db)
                if not info_found:
                    print("> 该餐盘未经历菜品购买阶段！请先购买菜品")
                    break

                plate.updateInfo(self.db)

            print("> 识别完成")
            self.end_flag = True

    def checkAnyWeight(self):
        weights = []
        for hx in self.hxs:
            weights.append(hx.get_weight_mean(5))

        got_weight = (np.array(weights) > -10)
        if np.all(got_weight == False):  # 全都未检测到重量
            print("> 无重量")
            return False
        return True


class CapProcess(Process):
    def __init__(self,
                 all_cap_queue: Queue,
                 recg_cap_queu: Queue,
                 device_id=0,
                 recg_freq=20):
        super().__init__()
        self.all_cap_queue = all_cap_queue
        self.recg_cap_queue = recg_cap_queu
        self.recg_freq = recg_freq
        self.device_id = device_id
        self.cap = cv2.VideoCapture(device_id)

    def run(self) -> None:
        frame_count = 0
        while True:
            ret, frame = self.cap.read()
            if not ret:
                print(f'[debug] No camera with device_id {self.device_id}')
                continue

            self.all_cap_queue.put(frame)
            frame_count += 1

            if frame_count % self.recg_freq == 0:
                self.recg_cap_queue.put(frame)

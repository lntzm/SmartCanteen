from plate import Plate
from database import Database
from ImageHandle import *
from hx711 import HX711
from baiduAPI import BaiduAPI
from wechatSubscribe import WechatSubscribe

import RPi.GPIO as GPIO
from multiprocessing import Process, Queue


class RecgProcess(Process):
    def __init__(self, img_queue: Queue):
        super().__init__()
        self.img_queue = img_queue
        self.start_enable = False
        self.end_flag = False

    def loadObject(self, db, wechatSubscribe):
        self.db = db
        hx1 = HX711(dout_pin=21, pd_sck_pin=20, offset=153430, ratio=424.79)
        hx2 = HX711(dout_pin=26, pd_sck_pin=19, offset=1451, ratio=430.58)
        hx3 = HX711(dout_pin=6, pd_sck_pin=5, offset=74428, ratio=432.34)
        self.hxs = [hx1, hx2, hx3]
        self.plates = [Plate(), Plate(), Plate()]
        self.got_weight = np.array([False, False, False])
        self.id_found = np.array([False, False, False])
        self.max_num_plates = len(self.hxs)
        self.wechatSubs = wechatSubscribe

    def run(self) -> None:
        while True:
            frame = self.img_queue.get()
            if self.end_flag:  # 完成了识别，需要拿走所有餐盘
                if self.checkAnyWeight():  # 还有重量，continue
                    print("> 请拿走餐盘")
                    continue
                else:  # 全部拿走了，开始下一轮识别
                    self.id_found = np.array([False, False, False])
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

            id_found = False
            info_found = False
            for i in range(self.max_num_plates):
                if not self.got_weight[i]:
                    continue
                plate = self.plates[i]
                if self.id_found[i]:
                    print(f"[debug] 压力传感器{i}对应餐盘已识别")
                    continue
                # img_b64 = CVEncodeb64(sync_imgs[i])
                print("> 开始识别餐盘id")
                id_found = self.plates[i].getID(sync_imgs[i])
                if not id_found:
                    print("  > 未发现餐盘id")
                    break
                print(f"  > 餐盘id: {plate.id}")

                info_found = plate.getInfoBefore(self.db)
                if not info_found:
                    print("> 该餐盘未经历菜品购买阶段！请先购买菜品")
                    break

                self.id_found[i] = True
                plate.updateInfo(self.db)

            if not id_found or not info_found:
                continue

            print("> 识别完成")
            self.wechatSubs.sendMsg("本次用餐结束", "快来看看您的本餐情况吧")
            self.end_flag = True

    def checkAnyWeight(self):
        weights = []
        for hx in self.hxs:
            weights.append(hx.get_weight_mean(5))
        print(weights)
        got_weight = (np.array(weights) > -10)
        if np.all(got_weight == False):  # 全都未检测到重量
            return False
        return True


class CapProcess(Process):
    def __init__(self,
                 img_queue: Queue,
                 camera_id,
                 recg_freq=15):
        super().__init__()
        self.img_queue = img_queue
        self.recg_freq = recg_freq
        self.camera_id = camera_id

    def loadObject(self, cap):
        self.cap = cap

    def run(self) -> None:
        frame_count = 0
        while True:
            ret, frame = self.cap.read()
            if not ret:
                print(f'[debug] No camera with device_id {self.camera_id}')
                continue
            frame_count += 1
            # cv2.imshow("client", frame)

            if frame_count == self.recg_freq:
                self.img_queue.put(frame)
                frame_count = 0


if __name__ == '__main__':
    GPIO.setmode(GPIO.BCM)
    db_ip = "192.168.43.1"
    camera_id = 0
    db = Database(f"mongodb://{db_ip}:27017/", "smartCanteen")
    wechatSubscribe = WechatSubscribe()
    cap = cv2.VideoCapture(camera_id)
    img_queue = Queue(1)
    cap_process = CapProcess(img_queue, camera_id)
    cap_process.loadObject(cap)
    recg_process = RecgProcess(img_queue)
    recg_process.loadObject(db, wechatSubscribe)

    cap_process.start()
    recg_process.start()

    # 等待进程2结束
    try:
        cap_process.join()
        recg_process.terminate()
    except KeyboardInterrupt:
        if cap_process.is_alive():
            cap_process.terminate()
        if recg_process.is_alive():
            recg_process.terminate()
    finally:
        GPIO.cleanup()
        cap.release()

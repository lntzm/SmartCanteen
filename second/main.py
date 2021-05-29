from second.plate2nd import Plate2nd
from database import Database
from ImageHandle import *
from second.hx711 import HX711

import RPi.GPIO as GPIO
import time
from multiprocessing import Process, Queue


def main_process(q):
    while True:
        frame = q.get()
        images, locs = splitImg(frame)

        if not images:
            print("分割不成功")
            continue
        if not hx1.get_weight_mean():
            print("分割区域未检测到重量")
            continue
        weights = []
        if hx1.get_weight_mean():
            weights.append(hx1.get_weight_mean)
        if hx2.get_weight_mean():
            weights.append(hx2.get_weight_mean)
        if hx3.get_weight_mean():
            weights.append(hx3.get_weight_mean)

        # 根据分割区域将重量与盘子对应
        num_conflict, weights = synchronize(locs, weights)
        if num_conflict:
            print("分割结果与重量检测不匹配")
            continue

        # 二次识别
        # 返回各分割图片识别结果
        for image, weight in images, weights:
            # 创建dish类和plate1st类
            plate = Plate2nd()
            # 是否找到该盘子记录
            if not plate.getID(image):
                continue

            if not plate.getInfoBefore():
                continue
            else:
                # 保存信息到本地数据库
                plate.rest_weight = weight
                # plate.saveInfo()
        # 识别结束，调用HTML网页显示

        # time.sleep(1)

if __name__ == '__main__':
    GPIO.setmode(GPIO.BCM)
    # 类的定义
    hx1 = HX711(dout_pin=21, pd_sck_pin=20, offset=31099, ratio=428.544)
    hx2 = HX711(dout_pin=26, pd_sck_pin=19, offset=31099, ratio=428.544)
    hx3 = HX711(dout_pin=6, pd_sck_pin=5, offset=31099, ratio=428.544)

    try:
        pass

    finally:
        GPIO.cleanup()

    db = Database("mongodb://localhost:27017/", "smartCanteen")
    cap = cv2.VideoCapture(0)
    # image_access_token = baiduAPI.fetchToken(baiduAPI.IMAGE_API_KEY, baiduAPI.IMAGE_SECRET_KEY)
    q = Queue()
    # 第二个进程，用于主程序运行
    process2 = Process(target=main_process, args=(q,))
    process2.start()

    accord = 0
    while True:
        ret, show = cap.read()
        if not ret:
            print('No camera')
            continue

        # 传递帧给main_process进程，这里取隔100帧发送一次
        if accord == 100:
            q.put(show)
            accord = 0
        else:
            accord += 1
        # cv2.namedWindow('image', cv2.WINDOW_NORMAL)
        # cv2.reszieWindow('image', 680, 400)
        cv2.imshow('image', show)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # 等待进程2结束
    process2.join()
    cap.release()
    cv2.destroyAllWindows()
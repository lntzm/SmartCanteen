from plate import Plate
from database import Database
from ImageHandle import *
from hx711 import HX711
from baiduAPI import BaiduAPI
from datetime import datetime

import RPi.GPIO as GPIO
import time
from multiprocessing import Process, Queue


def main_process(q):
    while True:
        frame = q.get()
        images, locs = splitImg(frame)

        if not images:
            print("> plates not detected")
            continue
        print("分割到", len(images), "个区域")

        weights = []
        hx1_weight = hx1.get_weight_mean(5)
        hx2_weight = hx2.get_weight_mean(5)
        hx3_weight = hx3.get_weight_mean(5)
        if hx1_weight:
            weights.append(hx1_weight)
            print("检测到1号盘子，重量为：", hx1_weight)

        if hx2_weight:
            weights.append(hx2_weight)
            print("检测到2号盘子，重量为：", hx2_weight)

        if hx3_weight:
            weights.append(hx3_weight)
            print("检测到3号盘子，重量为：", hx3_weight)

        # 根据分割区域将重量与盘子对应
        num_conflict, weights = synchronize(locs, weights)
        if num_conflict:
            print("分割结果与重量检测不匹配")
            continue

        id_found = False
        name_found = False
        # 二次识别
        # 返回各分割图片识别结果
        for image, weight in zip(images, weights):
            # 创建dish类和plate1st类
            plate = Plate()
            # 是否找到该盘子记录
            image_buffer = CVEncodeb64(image)
            print("> start getting IDs")
            id_found = plate.getID(baiduAPI, image_buffer)
            if not id_found:
                print("  > fail to recognize plate id")
                break
            print("  > plate id:", plate.id)

            plate_info = db.findPlate(plate.id)
            if not plate_info:
                print(" > plate hasn't recorded, error")
                continue
            elif plate_info['eaten']:
                plate.eaten = False
                print(" > plate was eaten, error")
                continue
            else:
                plate.eaten = True
                # 保存重量信息
                plate.rest_weight = weight
                time1st = datetime.strptime(plate_info['time'], '%Y-%m-%d')
                plate.updateTime(time1st)
                # 更新到本地数据库
                plate.updateInfo(db)
                # plate.saveInfo()
        # 识别结束，调用HTML网页显示

        # time.sleep(1)


if __name__ == '__main__':
    GPIO.setmode(GPIO.BCM)
    # 类的定义
    hx1 = HX711(dout_pin=21, pd_sck_pin=20, offset=68753, ratio=433.21)
    hx2 = HX711(dout_pin=26, pd_sck_pin=19, offset=-1660, ratio=430.05)
    hx3 = HX711(dout_pin=6, pd_sck_pin=5, offset=177856, ratio=424.71)

    db = Database("mongodb://localhost:27017/", "smartCanteen")
    baiduAPI = BaiduAPI()
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
import cv2
import numpy as np
import baiduAPI
from baiduAPI import BaiduAPI
from first.dish import Dish
from first.user import User
from first.plate1st import Plate1st
from database import Database
from ImageHandle import *
from multiprocessing import Process, Queue

def recognize(q):
    while True:
        frame = q.get()
        images = splitImg(frame)

        if not images:
            print("分割不成功")
            continue

        # 新的识别，添加一个判断是否为新用户，并创建一个user类
        print("分割成功，创建新的用户......")
        user = User()
        # 返回各分割图片识别结果
        for image in images:
            # 创建dish类和plate1st类
            dish = Dish()
            plate = Plate1st(dish.sumInfo(), user.sumInfo())
            image_buffer = CVEncodeb64(image)
            dish.RecognizeDish(baiduAPI, image_buffer)
            # 保存到本地数据库
            plate.saveInfo()

def display(q):
    pass


if __name__ == '__main__':
    db = Database("mongodb://localhost:27017/", "SmartCanteen")
    cap = cv2.VideoCapture(0)
    baiduAPI = BaiduAPI()
    # image_access_token = baiduAPI.fetchToken(baiduAPI.IMAGE_API_KEY, baiduAPI.IMAGE_SECRET_KEY)
    q = Queue()
    # 第二个进程，用于主程序运行
    recg_process = Process(target=recognize, args=(q,))
    recg_process.start()

    count = 0
    while True:
        ret, show = cap.read()
        if not ret:
            print('No camera')
            continue

        # 传递帧给main_process进程，这里取隔100帧发送一次
        if count == 100:
            q.put(show)
            count = 0
        else:
            count += 1
        # cv2.namedWindow('image', cv2.WINDOW_NORMAL)
        # cv2.reszieWindow('image', 680, 400)
        cv2.imshow('image', show)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # 等待进程2结束
    recg_process.join()
    cap.release()
    cv2.destroyAllWindows()
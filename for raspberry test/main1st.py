import cv2
import base64
import numpy as np
import baiduAPI
from baiduAPI import BaiduAPI
from dish import Dish
from user import User
from plate1st import Plate1st
from database import Database
from ImageHandle import *
from multiprocessing import Process, Queue

# from PIL import Image, ImageDraw, ImageFont
# import time
# import pandas as pd


def main_process(process_conn):
    while True:
        frame = process_conn.get()
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
            plate_info = plate.sumInfo()
            # print(plate_info)
            # 转码可以合并到splitimage()中
            image_buffer = CVEncodeb64(image)
            dish.RecognizeDish(baiduAPI, image_buffer)
            plate.getID(baiduAPI, image_buffer)

if __name__ == '__main__':
    db = Database("mongodb://localhost:27017/", "smartCanteen")
    cap = cv2.VideoCapture(0)
    baiduAPI = BaiduAPI()
    # image_access_token = baiduAPI.fetchToken(baiduAPI.IMAGE_API_KEY, baiduAPI.IMAGE_SECRET_KEY)
    process_conn = Queue()
    # 第二个进程，用于主程序运行
    process2 = Process(target=main_process, args=(process_conn,))
    process2.start()

    accord = 0
    while True:
        ret, show = cap.read()
        if not ret:
            print('No camera')
            continue

        # 传递帧给main_process进程，这里取隔100帧发送一次
        if accord == 100:
            process_conn.put(show)
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
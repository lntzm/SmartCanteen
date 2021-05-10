import cv2
import zmq
import base64
import time
from bluepy import btle
import numpy as np
import io
import picamera
import matplotlib.pyplot as plt
from PIL import Image
import baiduAPI
import pandas as pd
from PIL import Image, ImageDraw, ImageFont
import os
from multiprocessing import Process, Queue


# def b64EncodeCV(frame):
#     img = base64.b64decode(frame)
#     npimg = np.frombuffer(img, dtype=np.uint8)
#     return cv2.imdecode(npimg, 1)
#
#
# def b64EncodePIL(frame):
#     img = base64.b64decode(frame)
#     img = io.BytesIO(img)
#     img = Image.open(img)
#     return img

def CVEncodeb64(frame):
    encoded, buffer = cv2.imencode('.jpg', frame)
    return base64.b64encode(buffer)


def b64DecodeCV(frame):
    img = base64.b64decode(frame)
    npimg = np.frombuffer(img, dtype=np.uint8)
    return cv2.imdecode(npimg, 1)


def splitImg(image):
    # 先将图像转化成灰度，再转化成二值图像
    mask = cv2.cvtColor(image.copy(), cv2.COLOR_BGR2GRAY)
    _, mask = cv2.threshold(mask, 185, 255, cv2.THRESH_BINARY)
    # mask = cv2.erode(mask, None, iterations=2)
    # mask = cv2.dilate(mask, None, iterations=5)
    cv2.imwrite('mask.jpg', mask)
    # 检测边缘
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    images = []
    locs = []
    img_marked = image.copy()
    for c in contours:
        _, r = cv2.minEnclosingCircle(c)  # 找到最小圆，并返回圆心坐标和半径
        x, y, w, h = cv2.boundingRect(c)
        # x, y, r = (int(x), int(y), int(r))
        if 100 < r < 300:
            img_cut = image[y: y + h, x: x + w]
            # cv2.imwrite('img_cut.jpg', img_cut)
            images.append(img_cut)
            locs.append((x, y, w, h))
            img_marked = cv2.rectangle(img_marked, (x, y), (x + w, y + h), (0, 0, 255), 2)
            # img_marked = cv2.circle(img_marked, (x, y), r, (0, 0, 255), 2)

    # cv2.imshow('img_split', img_marked)
    cv2.imwrite('img_split.jpg', img_marked)
    return images, locs, img_marked


def mergeFirst(name, prob, calorie, info_first):
    # first.xlsx: eater_id, dish_id, name, prob, cal, weight, time
    nowStruct = time.localtime(int(time.time()))
    timeStr = time.strftime("%Y-%m-%d %H:%M:%S", nowStruct)
    if not calorie:
        calorie = np.nan
    value_first = [name, prob, calorie, timeStr]
    for i, key in enumerate(info_first.keys()):
        info_first[key].append(value_first[i])
    return info_first


def cv2AddChineseText(img, text, position, textColor=(255, 0, 0), textSize=15):
    if isinstance(img, np.ndarray):  # 判断是否OpenCV图片类型
        img = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
    # 创建一个可以在给定图像上绘图的对象
    draw = ImageDraw.Draw(img)
    # 字体的格式
    fontStyle = ImageFont.truetype("simsun.ttc", 16, encoding="utf-8")
    # 绘制文本
    draw.text(position, text, textColor, font=fontStyle)
    # 转换回OpenCV格式
    return cv2.cvtColor(np.asarray(img), cv2.COLOR_RGB2BGR)


def markInfo(image, infos, locs):
    infos = pd.DataFrame(infos)
    keys = infos.columns
    for index, loc in enumerate(locs):
        line = 0
        for j in range(infos.shape[1]):
            text = "{}: {}".format(keys[j], infos.iloc[index, j])
            # image = cv2.putText(
            #     image, text, (loc[0], loc[1]),
            #     cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
            image = cv2AddChineseText(image, text, (loc[0], loc[1] + line))
            line += 15
    return image


# def recognizeDish(info_first, images, image_access_token, img_marked, locs):
#     for image in images:
#         print("> recognizing")
#         name, prob, calorie = baiduAI.getDishResult(image_access_token, CVEncodeb64(image))
#         info_first = mergeFirst(name, prob, calorie, info_first)
#     img_marked = markInfo(img_marked, info_first, locs)
#     return info_first, img_marked

def recognizeDish(images, image_access_token):
    for image in images:
        print("> recognizing")
        name, prob, calorie = baiduAPI.getDishResult(image_access_token, CVEncodeb64(image))
    return name, prob, calorie


# 全局变量
image_access_token = baiduAPI.fetchToken(baiduAPI.IMAGE_API_KEY, baiduAPI.IMAGE_SECRET_KEY)


def screen_show(info_first):
    cap = cv2.VideoCapture(0)
    # 由q传递参数给第二个进程
    q = Queue()
    # 第二个进程，用于主程序运行
    thread2 = Process(target=main_process, args=(q, info_first,))
    thread2.start()

    while True:
        ret, show = cap.read()
        q.put(show)
        if not ret:
            print('No camera')
            continue
        # cv2.namedWindow('image', cv2.WINDOW_NORMAL)
        # cv2.reszieWindow('image', 680, 400)
        cv2.imshow('image', show)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    # 等待线程2结束
    thread2.join()
    cap.release()
    cv2.destroyAllWindows()


def main_process(q, info):
    while True:
        # cap = cv2.VideoCapture(0)
        # ret, frame = cap.read()
        # if not ret:
        #     print('No Camera')
        #     continue
        frame = q.get()
        images, locs, img_marked = splitImg(frame)

        if not images:
            # show = frame
            continue
        # info_first, img_marked = recognizeDish(info, images, image_access_token, img_marked, locs)
        name, prob, calorie = recognizeDish(images, image_access_token)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break


def main():
    keys_first = ['name', 'probability', 'calorie', 'time']
    # keys_second = ['name',  'time']
    # keys_result = ['name',  'calorie_get', 'start_time', 'eating_time']

    info_first = {key_first: [] for key_first in keys_first}
    # info_second = {key_second: [] for key_second in keys_second}

    # cap = cv2.VideoCapture(0)
    # ret, frame = cap.read()
    # _, show = cap.read()
    # 第一个进程，用于显示
    thread1 = Process(target=screen_show, args=(info_first,))
    thread1.start()
    # 等待线程1结束
    thread1.join()


if __name__ == '__main__':
    main()

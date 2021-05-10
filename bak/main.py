import os
import cv2
import base64
import time
import numpy as np
import io
import picamera
from PIL import Image
from multiprocessing import Process, Queue
from first.dish import Dish
from first.user import User
from first.plate1st import Plate1st
from database import Database


# 其他一些与流程相关的函数可以定义在这里
# 也可以新开文件去定义
# 或者放到现有的类里

def pay(dish_prices: float, user_balance: float, db: Database):
    """
    判断用户余额是否能够支付所有菜品，并扣除相应余额，更新数据库user集合
    :param dish_prices:
    :param user_balance:
    :param db:
    :return:
    """
    pass


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


# def cv2AddChineseText(img, text, position, textColor=(255, 0, 0), textSize=15):
#     if isinstance(img, np.ndarray):  # 判断是否OpenCV图片类型
#         img = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
#     # 创建一个可以在给定图像上绘图的对象
#     draw = ImageDraw.Draw(img)
#     # 字体的格式
#     fontStyle = ImageFont.truetype("simsun.ttc", 16, encoding="utf-8")
#     # 绘制文本
#     draw.text(position, text, textColor, font=fontStyle)
#     # 转换回OpenCV格式
#     return cv2.cvtColor(np.asarray(img), cv2.COLOR_RGB2BGR)
#
#
# def markInfo(image, infos, locs):
#     keys = infos.columns
#     for index, loc in enumerate(locs):
#         line = 0
#         for j in range(infos.shape[1]):
#             text = "{}: {}".format(keys[j], infos.iloc[index, j])
#             # image = cv2.putText(
#             #     image, text, (loc[0], loc[1]),
#             #     cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
#             image = cv2AddChineseText(image, text, (loc[0], loc[1] + line))
#             line += 15
#     return image

def CVEncodeb64(image):
    encoded, buffer = cv2.imencode('.jpg', image)
    return base64.b64encode(buffer)


def b64DecodeCV(image):
    img = base64.b64decode(image)
    npimg = np.frombuffer(img, dtype=np.uint8)
    return cv2.imdecode(npimg, 1)


def screen_show():
    cap = cv2.VideoCapture(0)
    # 由q传递参数给第二个进程
    q = Queue()
    # 第二个进程，用于主程序运行
    thread2 = Process(target=main_process, args=(q,))
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

def main_process(q):
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

        # 返回各分割图片识别结果
        for image in images:
            plate = Plate1st(dish.sumInfo(), user.sumInfo(), image)
            plate_info = plate.sumInfo()
            plate.dish.RecognizeDish(CVEncodeb64(image))
            # 盘子ID需要确定是否识别到
            no_dish_id = plate.RecognizeID(CVEncodeb64(image))

        # img_marked = markInfo(img_marked, plate_infos, locs)
        # 下一帧显示标记图像
        # show = img_marked

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

if __name__ == '__main__':
    user = User()
    dish = Dish()
    db = Database("mongodb://localhost:27017/", "smartCanteen")

    # init camera
    # cap = cv2.VideoCapture(0)
    # ret, frame = cap.read()
    # _, show = cap.read()
    # 第一个进程，用于主程序执行
    thread1 = Process(target=main_process, args=())
    thread1.start()
    # 等待线程1结束
    thread1.join()

    pass

from first.dish import Dish
from first.user import User
from first.plate1st import Plate1st
from database import Database
from ImageHandle import *

import cv2
from multiprocessing import Process, Queue


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
    # 检测边缘
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    images = []
    for c in contours:
        _, r = cv2.minEnclosingCircle(c)  # 找到最小圆，并返回圆心坐标和半径
        x, y, w, h = cv2.boundingRect(c)
        # x, y, r = (int(x), int(y), int(r))
        if 100 < r < 300:
            img_cut = image[y: y + h, x: x + w]
            # cv2.imwrite('img_cut.jpg', img_cut)
            images.append(img_cut)
    return images

def screen_show():
    cap = cv2.VideoCapture(0)
    # 由q传递参数给第二个进程
    q = Queue()
    # 第二个进程，用于主程序运行
    thread2 = Process(target=main_process, args=(q,))
    thread2.start()

    accord = 0

    while True:
        ret, show = cap.read()
        if not ret:
            print('No camera')
            continue

        # 传递帧给main_process进程，这里取隔5帧发送一次
        if accord == 5:
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
        images = splitImg(frame)

        if not images:
            # show = frame
            continue

        # 新的识别，添加一个判断是否为新用户，并创建一个user类
        user = User()
        # 返回各分割图片识别结果
        for image in images:
            # 创建dish类和plate1st类
            dish = Dish()
            plate = Plate1st(dish.sumInfo(), user.sumInfo())
            plate_info = plate.sumInfo()

            # 转码可以合并到splitimage()中
            image_buffer = CVEncodeb64(image)
            dish.RecognizeDish(image_buffer)
            plate.getID(image_buffer)
            pass

        # 中断应该screen_show内定义即可
        # if cv2.waitKey(1) & 0xFF == ord('q'):
        #     break


if __name__ == '__main__':
    # dish = Dish()
    # user = User()
    # plate = Plate1st(dish.sumInfo(), user.sumInfo())
    # plate_info = plate.sumInfo()
    db = Database("mongodb://localhost:27017/", "smartCanteen")

    # init camera
    # cap = cv2.VideoCapture(0)
    # ret, frame = cap.read()
    # _, show = cap.read()
    # 第一个进程，用于主程序执行
    thread1 = Process(target=main_process, args=())
    thread1.start()
    # 等待进程1结束
    thread1.join()

    pass

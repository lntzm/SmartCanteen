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


# TODO: 将多线程改为多进程
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
            # TODO: 重构以下逻辑
            # plate = Plate1st(dish.sumInfo(), user.sumInfo(), image)
            # plate_info = plate.sumInfo()

            # plate.dish.RecognizeDish(CVEncodeb64(image))
            #
            # # 盘子ID需要确定是否识别到
            # no_dish_id = plate.RecognizeID(CVEncodeb64(image))
            pass

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break


if __name__ == '__main__':
    dish = Dish()
    user = User()
    plate = Plate1st(dish.sumInfo(), user.sumInfo())
    plate_info = plate.sumInfo()
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

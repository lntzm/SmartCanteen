import cv2

from baiduAPI import BaiduAPI
from first.user import User
from first.plate import Plate
from database import Database
from ImageHandle import *
# import time

from multiprocessing import Process
from multiprocessing import Queue


def plateRecognize(q: Queue, control: Queue):
    while True:
        frame = q.get()
        if not control.get()[0]:
            if control.empty():
                control.put((False, True))  # 把取出来的再还回去
            print("[debug] plate: False")
            continue
        # time_start = time.time()
        images, img_marked = splitImg(frame)
        # time_end = time.time()
        # print('分割图片用时', time_end - time_start, 's')

        if not images:
            print("> 未发现餐盘")
            if control.empty():
                control.put((True, False))  # 未发现餐盘，继续进行餐盘识别进程
            continue
        # cv2.imwrite("img_marked.jpg", img_marked)
        print(f"> 发现了{len(images)}个餐盘")
        id_found = False
        name_found = False
        # 返回各分割图片识别结果
        for image in images:
            plate = Plate()
            image_buffer = CVEncodeb64(image)
            # time_start = time.time()
            print("> 开始检测餐盘id")
            id_found = plate.getID(baiduAPI, image_buffer)
            if not id_found:
                print("  > 未发现餐盘id")
                break
            print(f"  > 餐盘id: {plate.id}")
            # time_end = time.time()
            # print('ID识别用时', time_end - time_start, 's')
            if db.findPlate(plate.id) or db.findRecord(plate.id):
                print(f"> 该餐盘({plate.id})已经成功识别并记录")
                continue

            if db.findPlate(plate.id):
                print(f"> 请拿走餐盘({plate.id})")
                if control.empty():
                    control.put((True, False))  # 等待餐盘拿走，继续进行餐盘识别进程
                break

            # time_start = time.time()
            print("> 开始进行菜品识别")
            name_found = plate.getName(baiduAPI, image_buffer)
            if not name_found:
                print("  > 菜品识别失败")
                break
            print(f"  > 菜名:{plate.name}")
            # time_end = time.time()
            # print('菜品识别用时', time_end - time_start, 's')

            plate.searchDB(db)
            # 保存到本地数据库
            plate.saveInfo(db)

        if (not id_found) or (not name_found):
            if control.empty():
                control.put((False, True))  # 把取出来的再还回去
            continue

        # for循环中所有图片的id和name都识别到了
        # 发送给人脸识别进程True，可以开始人脸识别
        control.put((False, True))


def plateDisplay(q):
    count = 0
    while True:
        ret, show = plate_cap.read()
        if not ret:
            print('No camera')
            continue

        # 传递帧给main_process进程，这里取隔100帧发送一次zWASX
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


def userRecognize(q: Queue, control: Queue):
    while True:
        frame = q.get()
        if not control.get()[1]:
            control.put((True, False))  # 把取出来的再还回去
            print("[debug] user: False")
            continue

        user = User()
        print("> 开始人脸识别")
        found = user.getID(frame)
        if not found:
            if control.empty():
                control.put((True, False))  # 把取出来的再还回去
            print("  > 未找到用户")
            continue
        print(f"  > 用户id: {user.id}")

        # 写入数据库
        user.saveInfo(db)
        user.pay(db)

        db.commitRecord()
        db.pushRecord()
        db.cleanRecord()

        control.put((True, False))


def userDisplay(q):
    count = 0
    while face_cap.isOpened():
        ret, show = face_cap.read()
        if not ret:
            print('No camera')
            continue

        # 传递帧给main_process进程，这里取隔100帧发送一次
        if count == 20:
            q.put(show)
            count = 0
        else:
            count += 1
        cv2.imshow('face_detect', show)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break


if __name__ == '__main__':
    db = Database("mongodb://localhost:27017/", "SmartCanteen")
    plate_cap = cv2.VideoCapture(1)
    face_cap = cv2.VideoCapture(2)
    baiduAPI = BaiduAPI()
    plate_captures = Queue()
    face_captures = Queue()
    control = Queue(1)
    control.put((True, False))

    plate_disp_process = Process(target=plateDisplay, args=(plate_captures,))
    plate_recg_process = Process(target=plateRecognize, args=(plate_captures, control))
    user_disp_process = Process(target=userDisplay, args=(face_captures,))
    user_recg_process = Process(target=userRecognize, args=(face_captures, control))

    plate_disp_process.start()
    plate_recg_process.start()
    user_disp_process.start()
    user_recg_process.start()

    # 等待显示进程结束，结束后就关闭识别进程
    plate_disp_process.join()
    plate_recg_process.terminate()
    user_disp_process.join()
    user_recg_process.terminate()

    plate_cap.release()
    face_cap.release()
    cv2.destroyAllWindows()

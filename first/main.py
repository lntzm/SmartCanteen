from baiduAPI import BaiduAPI
from first.user import User
from first.plate import Plate
from database import Database
from ImageHandle import *

from multiprocessing import Process, Queue


def plateRecognize(q):
    while True:
        frame = q.get()
        images = splitImg(frame)

        if not images:
            continue

        # 新的识别，添加一个判断是否为新用户，并创建一个user类
        print("> plates detected")
        user = User()
        # 返回各分割图片识别结果
        for image in images:
            plate = Plate()
            image_buffer = CVEncodeb64(image)

            id_found = plate.getID(image_buffer)
            if not id_found:
                break
            if db.findPlate(plate.id):
                print("> plate already recorded, skip")
                continue
            name_found = plate.getName(baiduAPI, image_buffer)
            if not name_found:
                break

            plate.getWeight()
            plate.getPrice()

            # 保存到本地数据库
            plate.saveInfo()


def plateDisplay(q):
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


if __name__ == '__main__':
    db = Database("mongodb://localhost:27017/", "SmartCanteen")
    cap = cv2.VideoCapture(0)
    baiduAPI = BaiduAPI()
    plate_captures = Queue()
    face_captures = Queue()
    # 第二个进程，用于主程序运行
    plate_show_process = Process(target=plateDisplay, args=(plate_captures,))
    plate_recg_process = Process(target=plateRecognize, args=(plate_captures,))

    plate_show_process.start()
    plate_recg_process.start()


    # 等待进程2结束
    cap.release()
    cv2.destroyAllWindows()

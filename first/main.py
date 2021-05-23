from baiduAPI import BaiduAPI
# from first.user import User
from first.plate import Plate
from database import Database
from ImageHandle import *

from multiprocessing import Process, Queue, Pipe


def plateRecognize(q: Queue, pipe: Pipe()):
    while True:
        frame = q.get()
        images = splitImg(frame)

        if not images:
            print("> plates not detected")
            continue

        print("> plates detected")
        id_found = False
        name_found = False
        # 返回各分割图片识别结果
        for image in images:
            plate = Plate()
            image_buffer = CVEncodeb64(image)

            print("> start getting IDs")
            id_found = plate.getID(image)
            if not id_found:
                print("  > fail to recognize plate id")
                break
            print("  > plate id:", plate.id)
            if db.findPlate(plate.id):
                print("> plate already recorded, skip")
                continue

            print("> start getting dish name")
            name_found = plate.getName(baiduAPI, image_buffer)
            if not name_found:
                print("> fail to recognize dishes")
                break
            print("> name:{}, calories:{}".format(plate.name, plate.calories))

            plate.getWeight()
            plate.getPrice()

            # 保存到本地数据库
            plate.saveInfo()

        if (not id_found) or (not name_found):
            continue

        # 发送给人脸识别进程True，可以开始人脸识别
        pipe.send(True)


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


def userRecognize(q: Queue, pipe: Pipe()):
    while True:
        if not pipe.recv():
            continue

        pass


def userDisplay(q):
    pass


if __name__ == '__main__':
    db = Database("mongodb://localhost:27017/", "SmartCanteen")
    cap = cv2.VideoCapture("./2021-05-18 16-36-43.mkv")
    baiduAPI = BaiduAPI()
    plate_captures = Queue()
    face_captures = Queue()
    enable_send, enable_recv = Pipe()

    plate_disp_process = Process(target=plateDisplay, args=(plate_captures,))
    plate_recg_process = Process(target=plateRecognize, args=(plate_captures, enable_send))
    user_disp_process = Process(target=userDisplay, args=(face_captures,))
    user_recg_process = Process(target=userRecognize, args=(face_captures, enable_recv))

    plate_disp_process.start()
    plate_recg_process.start()
    user_disp_process.start()
    user_recg_process.start()

    # 等待显示进程结束，结束后就关闭识别进程
    plate_disp_process.join()
    plate_recg_process.terminate()
    user_disp_process.join()
    user_recg_process.terminate()

    cap.release()
    cv2.destroyAllWindows()

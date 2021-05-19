from plate2nd import Plate2nd
from database import Database
from ImageHandle import *
import first.main1st

def main_process(process_conn):
    while True:
        frame = process_conn.get()
        images = splitImg(frame)

        if not images:
            print("分割不成功")
            continue

        # 二次识别

        # 返回各分割图片识别结果
        for image in images:
            # 创建dish类和plate1st类
            plate = Plate2nd()
            # 是否找到该盘子记录
            plate.getID(image)
            if not plate.getInfoBefore():
                print("盘子编号：", plate.id, "，未识别到该盘子记录")
                continue
            else:
                # 保存到本地数据库
                plate.saveInfo()

if __name__ == '__main__':
    GPIO.setmode(GPIO.BCM)
    hx1 = HX711(dout_pin=21, pd_sck_pin=20, offset=31099, ratio=428.544)
    try:
        pass

    finally:
        GPIO.cleanup()

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
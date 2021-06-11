import cv2
import time
from ImageHandle import splitImg
from ImageHandle import CVEncodeb64
from baiduAPI import BaiduAPI

# from ImageHandle import *
# def QRcode(img):
#     detector = cv2.wechat_qrcode_WeChatQRCode("./detect.prototxt", "./detect.caffemodel", "./sr.prototxt", "./sr.caffemodel")
#     # 识别结果和位置
#     res, points = detector.detectAndDecode(img)
#     return res

cap = cv2.VideoCapture(2)
count = 0
start = 0
baiduAPI = BaiduAPI()
while True:

    ret, frame = cap.read()
    if not ret:
        print('No camera')
        continue
    # cv2.imwrite("test.jpg", frame)

    # if count % 2:
    #     start = time.time()
    # else:
    #     print(time.time()-start)



    imgs,_ = splitImg(frame)
    img = imgs[0]

    name, prob, _ = baiduAPI.getDishResult(CVEncodeb64(img))
    print(name, prob)
    cv2.imwrite("米饭4.jpg", img)
    break



    # cv2.imshow('client', frame)
    # count += 1

    # images, img_marked = splitImg(frame)
    # if not images:
    #     print("> plates not detected")
    #     continue
    #
    # for image in images:
    #     result = QRcode(image)
    #     print("图片返回结果为：", result)
    #
    # print("本次识别结束", len(images))
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()

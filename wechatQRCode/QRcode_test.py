import cv2
from ImageHandle import *
def QRcode(img):
    detector = cv2.wechat_qrcode_WeChatQRCode("./detect.prototxt", "./detect.caffemodel", "./sr.prototxt", "./sr.caffemodel")
    # 识别结果和位置
    res, points = detector.detectAndDecode(img)
    return res

cap = cv2.VideoCapture(0)
while True:
    ret, frame = cap.read()
    if not ret:
        print('No camera')
        continue
    cv2.imwrite("test.jpg", frame)
    cv2.imshow('client', frame)
    images, img_marked = splitImg(frame)
    if not images:
        print("> plates not detected")
        continue

    for image in images:
        result = QRcode(image)
        print("图片返回结果为：", result)

    print("本次识别结束", len(images))
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()

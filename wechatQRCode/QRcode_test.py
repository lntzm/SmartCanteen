import cv2

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

    cv2.imshow('client', frame)
    result = QRcode(frame)
    print(result)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()

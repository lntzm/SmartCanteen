import cv2
import base64


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


def CVEncodeb64(image):
    encoded, buffer = cv2.imencode('.jpg', image)
    return base64.b64encode(buffer)


def b64DecodeCV(image):
    img = base64.b64decode(image)
    npimg = np.frombuffer(img, dtype=np.uint8)
    return cv2.imdecode(npimg, 1)

import cv2
import base64


def splitImg(image):
    # 先将图像转化成灰度，再转化成二值图像
    mask = cv2.cvtColor(image.copy(), cv2.COLOR_BGR2GRAY)
    _, mask = cv2.threshold(mask, 185, 255, cv2.THRESH_BINARY)
    # mask = cv2.erode(mask, None, iterations=2)
    # mask = cv2.dilate(mask, None, iterations=5)
    cv2.imwrite('mask.jpg', mask)
    # 检测边缘
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    images = []
    locs = []
    img_marked = image.copy()
    for c in contours:
        _, r = cv2.minEnclosingCircle(c)  # 找到最小圆，并返回圆心坐标和半径
        x, y, w, h = cv2.boundingRect(c)
        # x, y, r = (int(x), int(y), int(r))
        if 100 < r < 300:
            img_cut = image[y: y + h, x: x + w]
            # cv2.imwrite('img_cut.jpg', img_cut)
            images.append(img_cut)
            locs.append((x, y, w, h))
            img_marked = cv2.rectangle(img_marked, (x, y), (x + w, y + h), (0, 0, 255), 2)
            # img_marked = cv2.circle(img_marked, (x, y), r, (0, 0, 255), 2)

    # cv2.imshow('img_split', img_marked)
    cv2.imwrite('img_split.jpg', img_marked)
    return images, locs, img_marked


def CVEncodeb64(image):
    encoded, buffer = cv2.imencode('.jpg', image)
    return base64.b64encode(buffer)


def b64DecodeCV(image):
    img = base64.b64decode(image)
    npimg = np.frombuffer(img, dtype=np.uint8)
    return cv2.imdecode(npimg, 1)

import cv2
import base64
import numpy as np


def splitImg(image):
    # 先将图像转化成灰度，再转化成二值图像
    mask = cv2.cvtColor(image.copy(), cv2.COLOR_BGR2GRAY)
    _, mask = cv2.threshold(mask, 185, 255, cv2.THRESH_BINARY)
    # 检测边缘
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    images = []
    locs = []
    for c in contours:
        _, r = cv2.minEnclosingCircle(c)  # 找到最小圆，并返回圆心坐标和半径
        x, y, w, h = cv2.boundingRect(c)
        # x, y, r = (int(x), int(y), int(r))
        if 100 < r < 300:
            img_cut = image[y: y + h, x: x + w]
            # cv2.imwrite('img_cut.jpg', img_cut)
            images.append(img_cut)
            locs.append((x, y, w, h))
    return images, locs


def CVEncodeb64(image):
    encoded, buffer = cv2.imencode('.jpg', image)
    return base64.b64encode(buffer)


def b64DecodeCV(image):
    img = base64.b64decode(image)
    npimg = np.frombuffer(img, dtype=np.uint8)
    return cv2.imdecode(npimg, 1)


# def synchronize(locs, weights):
#     num_conflict = False
#     if len(locs) != len(weights):
#         num_conflict = True
#         print("> numbers of splited images and weight sensors conflict")
#         return num_conflict, None
#
#     # get indexes of x in locs from small to large
#     # weight_sorts = sorted(range(len(locs)), key=lambda i: locs[i][0])
#     # weights = [weights[i] for i in weight_sorts]
#     locs_array = np.array([locs[i][0] for i in range(len(locs))])
#     locs_sorts = np.sort(locs_array)
#     weights_index = []
#     for loc in locs_array:
#         weights_index.append(np.where(locs_sorts == loc)[0][0])
#
#     weights = [weights[i] for i in weights_index]
#
#     return num_conflict, weights


def sortImgByHX711(images, locs, got_weight):
    sync_images = [None, None, None]
    locs_x = np.array(locs)[:, 0]
    # 根据locs_x的大小逆序对images排序
    images = np.array(images)[locs_x.argsort()[::-1]].tolist()
    index = 0
    for i in range(got_weight.size):
        if not got_weight[i]:
            continue
        sync_images[i] = images[index]
        index += 1
    return sync_images



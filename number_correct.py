# -*- coding: utf-8 -*-
"""
   File Name：     rotation_v3
   Description :
   date：          2019/5/10
"""
import cv2
import numpy as np
import matplotlib.pylab as plt
import time

def splitImg(image, debug=False):
    # 先将图像转化成灰度，再转化成二值图像
    mask = cv2.cvtColor(image.copy(), cv2.COLOR_BGR2GRAY)
    _, mask = cv2.threshold(mask, 80, 255, cv2.THRESH_BINARY)
    if debug:
        cv2.imwrite('mask.jpg', mask)
    # 检测边缘
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    images = []
    img_marked = image.copy()
    for c in contours:
        _, r = cv2.minEnclosingCircle(c)  # 找到最小圆，并返回圆心坐标和半径
        x, y, w, h = cv2.boundingRect(c)
        # x, y, r = (int(x), int(y), int(r))

        if 100 < r < 300:
            img_cut = image[y: y + h, x: x + w]
            cv2.imwrite('img_cut.jpg', img_cut)
            images.append(img_cut)
            img_marked = cv2.rectangle(img_marked, (x, y), (x + w, y + h), (0, 0, 255), 2)
            # img_marked = cv2.circle(img_marked, (x, y), int(r), (0, 0, 255), 2)
            print(r)
    return images, img_marked

image = cv2.imread('number110.png')
images, img_marked = splitImg(image, True)

if not images:
    print("> plates not detected")
cv2.imwrite("img_marked.jpg", img_marked)
print("分割到", len(images), "个区域")



# # img=img[14:-15,13:-14]
# gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
# ret, binary = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
#
# contours, hierarchy = cv2.findContours(binary, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
# print("num of contours: {}".format(len(contours)))
#
#
# rect = cv2.minAreaRect(contours[1])  #获取蓝色矩形的中心点、宽高、角度
# print(rect)
#
# '''
# retc=((202.82777404785156, 94.020751953125),
#  (38.13406753540039, 276.02105712890625),
#  -75.0685806274414)
# '''
#
# width = int(rect[1][0])
# height = int(rect[1][1])
# angle = rect[2]
# print(angle)
#
# if width < height:  #计算角度，为后续做准备
#   angle = angle - 90
# print(angle)
#
# # if  angle < -45:
# #     angle += 90.0
# #        #保证旋转为水平
# # width,height = height,width
# src_pts = cv2.boxPoints(rect)
#
# # box = cv2.boxPoints(rect)
# # box = np.int0(box)
# # cv2.drawContours(img_box, [box], 0, (0,255,0), 2)
# #
#
# dst_pts = np.array([[0, height],
#                     [0, 0],
#                     [width, 0],
#                     [width, height]], dtype="float32")
# M = cv2.getPerspectiveTransform(src_pts, dst_pts)
# warped = cv2.warpPerspective(img, M, (width, height))
#
# if angle<=-90:  #对-90度以上图片的竖直结果转正
#     warped = cv2.transpose(warped)
#     warped = cv2.flip(warped, 0)  # 逆时针转90度，如果想顺时针，则0改为1
#     # warped=warped.transpose
# cv2.imshow('wr1',warped)
# cv2.waitKey(0)
#

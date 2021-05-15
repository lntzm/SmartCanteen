import cv2
import numpy as np
import base64

"""
图片转base64类型模块
*转换为base64类型 才能上传到百度云API*
"""
def to_base64(img):
    ret, buf = cv2.imencode(".jpg", img)   # numpy图片转二进制
    img64 = base64.b64encode(buf)
    return str(img64, "utf-8")
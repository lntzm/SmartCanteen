import cv2
import numpy as np
from PIL import Image
import baiduAI
import pandas as pd
import main
from PIL import Image, ImageDraw, ImageFont

number_access_token = baiduAI.fetchToken(baiduAI.NUMBER_API_KEY, baiduAI.NUMBER_SECRET_KEY)

class PlateFirst:
    def __init__(self, dish: dict, user: dict, image: dict):
        self.id = 0             # 盘子ID
        self.eaten = False      # 第一次，没有吃过
        self.dish = dish        # 菜品信息
        self.user = user        # 用户信息
        self.image = image          # 第一次识别传入图片

        # 重命名dish和user中的键id
        self.dish["dish_id"] = self.dish.pop("_id")
        self.user["user_id"] = self.user.pop("_id")

    def RecognizeID(self, image):
        # ID识别获取盘子ID
        no_dish_id = False
        ID = baiduAI.getNumberResult(number_access_token, image)
        if not ID:
            print("> dish_id not found")
            no_dish_id = True
        return no_dish_id



        return no_dish_id, dish_ids

    def sumInfo(self):
        """
        将所有信息汇总成一个字典
        :return: 字典类型，所有成员变量
        """
        plate = {
            "_id": self.id,
            "eaten": self.eaten
        }
        plate.update(self.dish)
        plate.update(self.user)
        return plate

    def save(self):
        # 以plate为单位上传数据
        pass


    # def recognize(self):
    #     name, prob, calorie = baiduAI.getDishResult(image_access_token, CVEncodeb64(image))
    #     info_first = mergeFirst(name, prob, calorie, info_first)
    #
    #     self.dish.name = name
    #     self.dish.calories = calorie
    #
    #     assert isinstance(prob, object)
    #     probs.append(prob)
    #     info_firsts.append(info_first)
    #     calories.append(calorie)
    #
    #
    #     # cv2.namedWindow('image', cv2.WINDOW_NORMAL)
    #     # cv2.imshow('image', img_marked)
    #     return img_marked




    # def splitImg(image):
    #     # 先将图像转化成灰度，再转化成二值图像
    #     mask = cv2.cvtColor(image.copy(), cv2.COLOR_BGR2GRAY)
    #     _, mask = cv2.threshold(mask, 185, 255, cv2.THRESH_BINARY)
    #     # mask = cv2.erode(mask, None, iterations=2)
    #     # mask = cv2.dilate(mask, None, iterations=5)
    #     cv2.imwrite('mask.jpg', mask)
    #     # 检测边缘
    #     contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    #
    #     images = []
    #     locs = []
    #     img_marked = image.copy()
    #     for c in contours:
    #         _, r = cv2.minEnclosingCircle(c)  # 找到最小圆，并返回圆心坐标和半径
    #         x, y, w, h = cv2.boundingRect(c)
    #         # x, y, r = (int(x), int(y), int(r))
    #         if 100 < r < 300:
    #             img_cut = image[y: y + h, x: x + w]
    #             # cv2.imwrite('img_cut.jpg', img_cut)
    #             images.append(img_cut)
    #             locs.append((x, y, w, h))
    #             img_marked = cv2.rectangle(img_marked, (x, y), (x + w, y + h), (0, 0, 255), 2)
    #             # img_marked = cv2.circle(img_marked, (x, y), r, (0, 0, 255), 2)
    #
    #     # cv2.imshow('img_split', img_marked)
    #     cv2.imwrite('img_split.jpg', img_marked)
    #     return images, locs, img_marked

    def mergeFirst(name, prob, calorie, info_first):
        # 合并第一次识别信息
        # first.xlsx: eater_id, dish_id, name, prob, cal, weight, time
        nowStruct = time.localtime(int(time.time()))
        timeStr = time.strftime("%Y-%m-%d %H:%M:%S", nowStruct)
        if not calorie:
            calorie = np.nan
        value_first = [name, prob, calorie, timeStr]
        for i, key in enumerate(info_first.keys()):
            info_first[key].append(value_first[i])
        return info_first


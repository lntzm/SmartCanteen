# -*- coding: utf-8 -*-

import os
import json
import base64
import time
from urllib.request import urlopen
from urllib.request import Request
from urllib.error import URLError
from urllib.parse import urlencode
import ssl
import requests
import cv2


class BaiduAPI:
    def __init__(self):
        ssl._create_default_https_context = ssl._create_unverified_context  # 防止https证书校验不正确
        self.IMAGE_API_KEY = 'FPqEAsBw7BKAKyPaanpVo8rE'
        self.IMAGE_SECRET_KEY = 'pNPM0mZCQisyuXostxWX3QdFQZ2p3el8'

        self.ID_API_KEY = 'Ogq6rapwYUzn679qjM2BYIrG'
        self.ID_SECRET_KEY = 'SjXDBkNeiqI2nYeNDXe28nPZcyAVoEmj'

        self.DISH_URL = "https://aip.baidubce.com/rest/2.0/image-classify/v2/dish"
        self.QRCODE_URL = "https://aip.baidubce.com/rest/2.0/ocr/v1/qrcode"
        self.NUMBER_URL = "https://aip.baidubce.com/rest/2.0/ocr/v1/numbers"

        self.TOKEN_URL = 'https://aip.baidubce.com/oauth/2.0/token'

    # start modifying
    def fetchToken(self, API_KEY, SECRET_KEY):
        """
            获取access_token
        """
        params = {'grant_type': 'client_credentials',
                  'client_id': API_KEY,
                  'client_secret': SECRET_KEY}
        post_data = urlencode(params).encode('utf-8')
        req = Request(self.TOKEN_URL, post_data)
        f = urlopen(req, timeout=5)
        result_str = f.read().decode()
        result = json.loads(result_str)

        if 'access_token' in result.keys() and 'scope' in result.keys():
            if 'brain_all_scope' not in result['scope'].split(' '):
                raise KeyError('no brain_all_scope, please check the ability')
            # 拼接图像识别url
            return result['access_token']
        else:
            raise KeyError('wrong API_KEY or SECRET_KEY')

    def request(self, url, data):
        """
            调用远程服务
        """
        req = Request(url, data.encode('utf-8'))
        f = urlopen(req)
        result_str = f.read().decode()
        return result_str

    def getDishResult(self, image):
        """
            调用菜品识别接口并获得结果
        """
        access_token = self.fetchToken(self.IMAGE_API_KEY, self.IMAGE_SECRET_KEY)
        request_url = self.DISH_URL + "?access_token=" + access_token
        params = {'image': image, 'top_num': 1}
        data = urlencode(params).encode('utf-8')
        headers = {'content-type': 'application/x-www-form-urlencoded'}
        req = Request(url=request_url, data=data, headers=headers)
        response = urlopen(req).read().decode()
        result_json = json.loads(response)

        if 'error_code' in result_json.keys():
            print("> ERROR: ", result_json['error_msg'])
            if result_json['error_code'] == 18:
                print("  request too fast, sleep 1s.")
                time.sleep(1)
                return None, None, None

        # 获得图片结果
        for data in result_json["result"]:
            if data[u'has_calorie']:
                return data['name'], round(float(data['probability']), 3), data['calorie']
            else:
                return data['name'], data['probability'], None

    def getNumberResult(self, image):
        """
            调用数字识别接口并获得结果
        """
        access_token = self.fetchToken(self.ID_API_KEY, self.ID_SECRET_KEY)
        request_url = self.NUMBER_URL + "?access_token=" + access_token
        params = {'image': image}
        data = urlencode(params).encode('utf-8')
        headers = {'content-type': 'application/x-www-form-urlencoded'}
        req = Request(url=request_url, data=data, headers=headers)
        response = urlopen(req).read().decode()
        result_json = json.loads(response)

        if 'error_code' in result_json.keys():
            print("> ERROR: ", result_json['error_msg'])
            return None

        if result_json['words_result_num'] == 1:
            return result_json['words_result'][0]['words']
        else:
            return None

    def getQRCodeResult(self, image):
        access_token = self.fetchToken(self.ID_API_KEY, self.ID_SECRET_KEY)
        request_url = self.QRCODE_URL + "?access_token=" + access_token
        params = {'image': image}
        # data = urlencode(params).encode('utf-8')
        headers = {'content-type': 'application/x-www-form-urlencoded'}
        response = requests.post(request_url, data=params, headers=headers)
        result = response.json()
        if 'error_code' in result.keys():
            print("[ERROR] in BaiduAPI.getQRCodeResult(): ", result['error_msg'])
            return None

        if result['codes_result_num'] == 1:
            return result['codes_result'][0]['text'][0]
        else:
            print(f"[ERROR] in BaiduAPI.getQRCodeResult(): get {result['codes_result_num']} results")
            return None


if __name__ == '__main__':
    # file_path = '/home/lzh/Desktop/temp'
    baiduAI = BaiduAPI()
    #
    # # 检查文件是否存在
    # if not os.path.exists(file_path):
    #     raise FileNotFoundError("{} not exist".format(file_path))
    # try:
    #     images = os.listdir(file_path)
    # except NotADirectoryError:
    #     images = [os.path.basename(file_path)]
    #     file_path = os.path.dirname(file_path)
    #
    # for image in images:
    #     # 获取图片
    #     with open(os.path.join(file_path, image), 'rb')as f:
    #         print('{}'.format(image))
    #         image = base64.b64encode(f.read())
    #     # print("> start recognizing {}".format(image))
    #     name, prob, calorie = baiduAI.getDishResult(image)
    #     print(u"  name: {}, probability: {}, calorie: {} Cal/100g"
    #           .format(name, prob, calorie))
    #     time.sleep(0.5)
    img = cv2.imread('./test.png')
    encoded, buffer = cv2.imencode('.jpg', img)
    img = base64.b64encode(buffer)
    result = baiduAI.getQRCodeResult(img)
    pass

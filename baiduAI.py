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

ssl._create_default_https_context = ssl._create_unverified_context  # 防止https证书校验不正确

IMAGE_API_KEY = 'FPqEAsBw7BKAKyPaanpVo8rE'
IMAGE_SECRET_KEY = 'pNPM0mZCQisyuXostxWX3QdFQZ2p3el8'

NUMBER_API_KEY = 'Ogq6rapwYUzn679qjM2BYIrG'
NUMBER_SECRET_KEY = 'SjXDBkNeiqI2nYeNDXe28nPZcyAVoEmj'

IMAGE_RECOGNIZE_URL = "https://aip.baidubce.com/rest/2.0/image-classify/v2/dish"

QRCODE_URL = "https://aip.baidubce.com/rest/2.0/ocr/v1/qrcode"

NUMBER_URL = "https://aip.baidubce.com/rest/2.0/ocr/v1/numbers"

TOKEN_URL = 'https://aip.baidubce.com/oauth/2.0/token'


# def fetchToken():
#     """
#         获取access_token
#     """
#     params = {'grant_type': 'client_credentials',
#               'client_id': API_KEY,
#               'client_secret': SECRET_KEY}
#     post_data = urlencode(params).encode('utf-8')
#     req = Request(TOKEN_URL, post_data)
#     f = urlopen(req, timeout=5)
#     result_str = f.read().decode()
#     result = json.loads(result_str)
#
#     if 'access_token' in result.keys() and 'scope' in result.keys():
#         if 'brain_all_scope' not in result['scope'].split(' '):
#             raise KeyError('no brain_all_scope, please check the ability')
#         # 拼接图像识别url
#         request_url = IMAGE_RECOGNIZE_URL + "?access_token=" + result['access_token']
#     else:
#         raise KeyError('wrong API_KEY or SECRET_KEY')
#
#     return request_url
#
#
# def request(url, data):
#     """
#         调用远程服务
#     """
#     req = Request(url, data.encode('utf-8'))
#     f = urlopen(req)
#     result_str = f.read().decode()
#     return result_str
#
#
# def getResult(request_url, image):
#     """
#         调用菜品识别接口并获得结果
#     """
#     params = {'image': image, 'top_num': 1}
#     data = urlencode(params).encode('utf-8')
#     headers = {'content-type': 'application/x-www-form-urlencoded'}
#     req = Request(url=request_url, data=data, headers=headers)
#
#     response = urlopen(req).read().decode()
#     result_json = json.loads(response)
#
#     if 'error_code' in result_json.keys():
#         print("> ERROR: ", result_json['error_msg'])
#         if result_json['error_code'] == 18:
#             print("  request too fast, sleep 3s.")
#             time.sleep(3)
#             return None, None, None
#
#     # 获得图片结果
#     for data in result_json["result"]:
#         if data[u'has_calorie']:
#             return data['name'], round(float(data['probability']), 3), data['calorie']
#         else:
#             return data['name'], data['probability'], None

# start modifying
def fetchToken(API_KEY, SECRET_KEY):
    """
        获取access_token
    """
    params = {'grant_type': 'client_credentials',
              'client_id': API_KEY,
              'client_secret': SECRET_KEY}
    post_data = urlencode(params).encode('utf-8')
    req = Request(TOKEN_URL, post_data)
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


def request(url, data):
    """
        调用远程服务
    """
    req = Request(url, data.encode('utf-8'))
    f = urlopen(req)
    result_str = f.read().decode()
    return result_str


def getDishResult(access_token, image):
    """
        调用菜品识别接口并获得结果
    """
    request_url = IMAGE_RECOGNIZE_URL + "?access_token=" + access_token
    params = {'image': image, 'top_num': 1}
    data = urlencode(params).encode('utf-8')
    headers = {'content-type': 'application/x-www-form-urlencoded'}
    req = Request(url=request_url, data=data, headers=headers)

    response = urlopen(req).read().decode()
    result_json = json.loads(response)

    if 'error_code' in result_json.keys():
        print("> ERROR: ", result_json['error_msg'])
        if result_json['error_code'] == 18:
            print("  request too fast, sleep 3s.")
            time.sleep(3)
            return None, None, None

    # 获得图片结果
    for data in result_json["result"]:
        if data[u'has_calorie']:
            return data['name'], round(float(data['probability']), 3), data['calorie']
        else:
            return data['name'], data['probability'], None


def getNumberResult(access_token, image):
    """
        调用数字识别接口并获得结果
    """
    request_url = NUMBER_URL + "?access_token=" + access_token
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


if __name__ == '__main__':
    file_path = '/home/lzh/Desktop/temp'
    image_access_token = fetchToken(IMAGE_API_KEY, IMAGE_SECRET_KEY)

    # 检查文件是否存在
    if not os.path.exists(file_path):
        raise FileNotFoundError("{} not exist".format(file_path))
    try:
        images = os.listdir(file_path)
    except NotADirectoryError:
        images = [os.path.basename(file_path)]
        file_path = os.path.dirname(file_path)

    for image in images:
        # 获取图片
        with open(os.path.join(file_path, image), 'rb')as f:
            print('{}'.format(image))
            image = base64.b64encode(f.read())
        # print("> start recognizing {}".format(image))
        name, prob, calorie = getDishResult(image_access_token, image)
        print(u"  name: {}, probability: {}, calorie: {} Cal/100g"
              .format(name, prob, calorie))
        time.sleep(0.5)

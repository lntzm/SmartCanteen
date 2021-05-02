import cv2
import numpy as np

from aip import AipFace

from utils import to_base64, take_photo
from utils import judge_face, crop_face
from utils import det_options, register_options

# 百度云API参数
APP_ID = '23931013'
API_KEY = 'ztwX2ncIovCAKfSPcdfoxdEj'
SECRET_KEY = 'vfrRf1qdrwPq2oUpOg0DzNRmAp79mUDF'
image_type = "BASE64"

"""
python-sdk tutorial
https://ai.baidu.com/ai-doc/FACE/ek37c1qiz#%E5%AE%89%E8%A3%85%E4%BA%BA%E8%84%B8%E8%AF%86%E5%88%AB-python-sdk
"""

class FaceRCN():

    def __init__(self):
        # 建立一个人脸API的对象
        self.client = AipFace(APP_ID, API_KEY, SECRET_KEY)

    """
    人脸检测
    *检测图片中的人脸 并返回人脸信息*

    img_rgb: RGB格式图片(numpy array)
    face_field: 人脸检测选项  beauty(颜值)  quality(人脸质量)
    """
    def face_detect(self, img_rgb, face_field="beauty,quality"):

        img64 = to_base64(img_rgb)
        det_options["face_field"] = face_field
        face_result = self.client.detect(img64, image_type, det_options)

        if face_result["error_msg"] == "SUCCESS":
            return face_result["result"]["face_list"][0]
        else:
            return None

    """
    人脸注册
    *对符合要求的人脸 注册到人脸库*

    img_rgb: RGB格式图片(numpy array)
    group_id: 人脸库分组
    user_id: 人脸库中用户id
    user_info: 用户备注
    mode: 注册模式为附加
    """
    # 人脸注册
    def face_register(self,
                    img_rgb, 
                    group_id, 
                    user_id, 
                    user_info="user's info", 
                    mode = "APPEND"):

        # 获取人脸检测结果
        face_list = self.face_detect(img_rgb, face_field="quality")

        # 判断人脸质量
        if face_list is not None:
            """
            detail_info 包含了人脸中哪些项的质量没有合格 是一个字典
            比如可以用于小程序提醒用户正确地拍人脸照 如：站到更亮的地方
            具体可以见 utils.face_utils.judge_face()
            """
            detailed_info = judge_face(face_list, detailed=True)
            admission = detailed_info["admission"]
        else:
            admission = False

        """人脸注册部分"""
        if admission:
            # 裁剪人脸
            face_cropped = crop_face(img_rgb, face_list, admission=admission)

            # 注册选项：1. 用户备注 2. 注册模式为附加
            register_options["user_info"] = user_info
            register_options["action_type"] = mode

            # 带参数调用API进行人脸注册
            face_result = self.client.addUser(face_cropped, image_type, group_id, user_id, register_options)

            if face_result["error_msg"] == "SUCCESS":
                # 注册成功
                print("Registration success!")
                return face_result
        elif face_list is not None:
            # 人脸质量不过关
            print("Face quality does not meet the requirements.")
            return detailed_info
        else:
            # 根本就没有人脸ヽ(`Д´)ﾉ
            print("Face not detected!")
            return None

    """
    人脸搜索
    *在人脸库中找到输入的人脸 并返回用户信息*

    img_rgb: RGB格式图片(numpy array)
    group_id: 人脸库分组
    """
    def face_search(self, img_rgb, group_id):     

        img64 = to_base64(img_rgb)
        # 调API在人脸库进行搜索
        face_result =  self.client.search(img64, image_type, group_id)

        if face_result["error_msg"] == "SUCCESS":
            print("User found!")
            return face_result["result"]["user_list"][0]
        else:
            # 没有这个用户 建议赶紧注册！(o°ω°o)
            print("User not found!")
            return None







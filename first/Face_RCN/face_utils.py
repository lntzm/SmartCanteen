import cv2
import numpy as np
import base64

"""人脸检测部分"""
det_options = {}
det_options["face_field"] = "beauty,quality"    # 返回颜值 人脸质量
det_options["max_face_num"] = 1                 # 人脸检测数
det_options["face_type"] = "LIVE"               # 相机拍摄风格
det_options["liveness_control"] = "LOW"         # 活体检测

"""人脸注册部分"""
register_options = {}
register_options["user_info"] = "user's info"       # 用户信息  
register_options["quality_control"] = "NORMAL"      # 人脸质量控制
register_options["liveness_control"] = "LOW"        # 活体检测
register_options["action_type"] = "APPEND"          # 已注册 则在该用户尾部追加新的人脸

"""人脸搜索部分"""
search_options = {}
search_options["match_threshold"] = 90              # 默认80 最大100

user_dict = {
    "ydj": "杨东杰",
    "xbc": "许柏城",
    "lzh": "刘知航",
    "qsy": "钱双熠",
    "wtq": "吴天琪"
}

"""
#################################################
人脸搜索相关函数
"""
ID = '23931013'
KEY = 'ztwX2ncIovCAKfSPcdfoxdEj'
S_KEY = 'vfrRf1qdrwPq2oUpOg0DzNRmAp79mUDF'
face_config = (ID, KEY, S_KEY)
image_type = "BASE64"


def to_base64(img):
    ret, buf = cv2.imencode(".jpg", img)   # numpy图片转二进制
    img64 = base64.b64encode(buf)
    return str(img64, "utf-8")

"""人脸质量判断"""
def judge_face(face_list, detailed=False):
    occulsion = all([v < 0.6 for v in face_list["quality"]["occlusion"].values()]) # 判断脸上是否有遮盖
    blur = face_list["quality"]["blur"] < 0.7  # 判断人脸是否清晰
    angle = all([abs(v) < 20 for v in face_list["angle"].values()]) # 判断脸的三维旋转角度是否小于20
    completeness = face_list["quality"]["completeness"] > 0.8   # 判断脸是否完整
    illumination = face_list["quality"]["illumination"] > 40    # 判断光照
    
    face_width = face_list["location"]["width"] > 100   # 人脸照片宽度大于100
    face_height = face_list["location"]["height"] > 100 # 人脸照片高度大于100
    face_area = face_width and face_height

    # 判断人脸是否符合人脸注册的标准
    admission_flag = occulsion and blur and angle and completeness and illumination and face_area
    
    if not detailed:
        return admission_flag
    else:
        # detail_info 返回了人脸中哪些项的质量没有合格
        detailed_info = {
            "admission": admission_flag,
            "occulsion": occulsion,
            "blur": blur,
            "angle": angle,
            "completeness": completeness,
            "illumination": illumination,
            "face_area": face_area
        }

        return detailed_info

"""人脸裁剪"""
def crop_face(img, face_list, admission=True):
    if admission:
        loc = face_list["location"]
        left, top, width, height, rotation = [round(v) for v in loc.values()] # 获取人脸位置
        face_img = img[top:top + height, left:left + width, :] # 裁剪人脸
        return to_base64(face_img)
    else:
        return None
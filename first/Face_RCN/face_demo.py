import os
import sys
sys.path.append(os.path.abspath(os.path.dirname(__file__) + '/' + '..'))

from utils.take_photo import take_photo
from Face_RCN.FaceRCN import FaceRCN

def main():
    # 建立一个人脸检测对象
    faceRCN = FaceRCN()

    # 打开相机 按esc拍一张照
    img_rgb1 = take_photo(cam_id=0)
    print("---------------------------")
    # 人脸注册 
    user_id = "dj"  ### 注意改user_id !!! ###

    register_result = faceRCN.face_register(img_rgb1, group_id="test", user_id = user_id)
    print("\nregister_result:")
    print(register_result)
    print("\n")

    # 打开相机 按esc拍一张照
    img_rgb2 = take_photo(cam_id=0)
    print("---------------------------")
    # 人脸搜索
    search_result = faceRCN.face_search(img_rgb2, group_id="test")
    print("\nsearch_result:")
    print(search_result)

    # 人脸检测
    detect_result = faceRCN.face_detect(img_rgb2)
    # 打印颜值分数
    if detect_result is not None:
        print("\nBeauty score:" + str(detect_result["beauty"]))

if __name__ == "__main__":
    main()
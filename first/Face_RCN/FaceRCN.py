import cv2
import numpy as np
from first.Face_RCN.retinaface import Retinaface
from aip import AipFace

import time
from first.Face_RCN.face_utils import *

class FaceRCN():

    def __init__(self, face_choice = "Retina"):
        self.face_init()
        if(face_choice == "Retina"):
            self.client = Retinaface()
        else:
            self.client = self._aip

    """
    人脸检测
    *检测图片中的人脸 并返回人脸信息*

    --input:
        img_rgb: RGB格式图片(numpy array)
        face_field: 人脸检测选项  beauty(颜值)  quality(人脸质量)
    --output:
        返回带有人脸信息的字典
    """
    def face_detect(self, img_rgb, face_field="beauty,quality"):

        img64 = to_base64(img_rgb)
        self.client = self._aip
        det_options["face_field"] = face_field

        face_result = self.client.detect(img64, image_type, det_options)

        if face_result["error_msg"] == "SUCCESS":
            return face_result["result"]["face_list"][0]
        else:
            return None

    def face_init(self):
        self._aip = AipFace(*face_config)

    """
    人脸注册
    *对符合要求的人脸 注册到人脸库*

    --input:
        img_rgb: RGB格式图片(numpy array)
        group_id: 人脸库分组
        user_id: 人脸库中用户id
        user_info: 用户备注
        mode: 注册模式为附加
    --output；
        注册成功： 返回人脸信息
        注册失败（人脸不合格）： 返回人脸质量不合格的项目列表
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
            self.client = self._aip

            # 注册选项：1. 用户备注 2. 注册模式为附加
            register_options["user_info"] = user_info
            register_options["action_type"] = mode

            # 带参数进行人脸注册
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

    --input:
        img_rgb: RGB格式图片(numpy array)
        group_id: 人脸库分组
    --output:
        人脸搜索结果的字典 包括了用户id的key
    """
    def face_search(self, img_rgb, group_id):     

        img64 = to_base64(img_rgb)
        self.client = self._aip
        # 在人脸库进行搜索
        face_result =  self.client.search(img64, image_type, group_id, search_options)

        if face_result["error_msg"] == "SUCCESS":
            face_user = face_result["result"]["user_list"][0]
            return user_dict[face_user["user_id"]]
        else:
            # 没有这个用户 建议赶紧注册！(o°ω°o)
            return None

#-------------------------------------------------------------------------#
#   人脸测试
#-------------------------------------------------------------------------#

if __name__ == "__main__":
    retinaface = Retinaface()
    #-------------------------------------------------------------------------#
    #   mode用于指定测试的模式：
    #   'predict'表示单张图片预测
    #   'video'表示视频检测
    #   'fps'表示测试fps
    #-------------------------------------------------------------------------#
    mode = "predict"
    #-------------------------------------------------------------------------#
    #   video_path用于指定视频的路径，当video_path=0时表示检测摄像头
    #   video_save_path表示视频保存的路径，当video_save_path=""时表示不保存
    #   video_fps用于保存的视频的fps
    #   video_path、video_save_path和video_fps仅在mode='video'时有效
    #   保存视频时需要ctrl+c退出才会完成完整的保存步骤，不可直接结束程序。
    #-------------------------------------------------------------------------#
    video_path      = 0
    video_save_path = ""
    video_fps       = 25.0

    if mode == "predict":
        '''
        1、无法进行批量预测，如果想要批量预测，可以利用os.listdir()遍历文件夹，利用cv2.imread打开图片文件进行预测。
        2、如果想要保存，利用cv2.imwrite("img.jpg", r_image)即可保存。
        3、如果想要获得框的坐标，可以进入detect_image函数，读取(b[0], b[1]), (b[2], b[3])这四个值。
        4、如果想要截取下目标，可以利用获取到的(b[0], b[1]), (b[2], b[3])这四个值在原图上利用矩阵的方式进行截取。
        5、在更换facenet网络后一定要重新进行人脸编码，运行encoding.py。
        '''
        while True:
            img = input('Input image filename:')
            image = cv2.imread(img)
            if image is None:
                print('Open Error! Try again!')
                continue
            else:
                image   = cv2.cvtColor(image,cv2.COLOR_BGR2RGB)
                r_image = retinaface.detect_image(image)
                r_image = cv2.cvtColor(r_image,cv2.COLOR_RGB2BGR)
                cv2.imshow("after",r_image)
                cv2.waitKey(0)

    elif mode == "video":
        capture = cv2.VideoCapture(video_path)
        if video_save_path!="":
            fourcc = cv2.VideoWriter_fourcc(*'XVID')
            size = (int(capture.get(cv2.CAP_PROP_FRAME_WIDTH)), int(capture.get(cv2.CAP_PROP_FRAME_HEIGHT)))
            out = cv2.VideoWriter(video_save_path, fourcc, video_fps, size)

        fps = 0.0
        while(True):
            t1 = time.time()
            # 读取某一帧
            ref,frame=capture.read()
            # 格式转变，BGRtoRGB
            frame = cv2.cvtColor(frame,cv2.COLOR_BGR2RGB)
            # 进行检测
            frame = np.array(retinaface.detect_image(frame))
            # RGBtoBGR满足opencv显示格式
            frame = cv2.cvtColor(frame,cv2.COLOR_RGB2BGR)
                    
            fps  = ( fps + (1./(time.time()-t1)) ) / 2
            print("fps= %.2f"%(fps))
            frame = cv2.putText(frame, "fps= %.2f"%(fps), (0, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            
            cv2.imshow("video",frame)
            c= cv2.waitKey(1) & 0xff 
            if video_save_path!="":
                out.write(frame)

            if c==27:
                capture.release()
                break
        capture.release()
        out.release()
        cv2.destroyAllWindows()

    elif mode == "fps":
        test_interval = 100
        img = cv2.imread('img/obama.jpg')
        img = cv2.cvtColor(img,cv2.COLOR_BGR2RGB)
        tact_time = retinaface.get_FPS(img, test_interval)
        print(str(tact_time) + ' seconds, ' + str(1/tact_time) + 'FPS, @batch_size 1')
    else:
        raise AssertionError("Please specify the correct mode: 'predict', 'video' or 'fps'.")
from datetime import datetime
import cv2


class Plate:
    def __init__(self):
        self.id = 0  # 盘子ID
        self.eaten = True  # 第二次，已经吃过
        self.rest_weight = 0  # 剩余重量
        self.__db_info = None
        self.end_time = ""  # 二次记录时间
        self.meal_time = 0  # 用餐时长
        self.QRCodeDetector = cv2.wechat_qrcode_WeChatQRCode("./wechatQRCode/detect.prototxt",
                                                             "./wechatQRCode/detect.caffemodel",
                                                             "./wechatQRCode/sr.prototxt",
                                                             "./wechatQRCode/sr.caffemodel")

    def getID(self, img):
        """
        二维码识别获取盘子ID
        :param image: 输入图片
        :return 是否成功获取盘子ID
        """
        # self.id = baiduAPI.getNumberResult(image_buffer)
        res, _ = self.QRCodeDetector.detectAndDecode(img)
        if not res:
            return False
        self.id = res[0]
        return True

    def getWeight(self, hx711):
        """
        称重获取剩余重量
        :param
        :return:
        """
        weight = hx711.get_weight_mean(5)
        self.rest_weight = 0 if -10 < weight < 0 else weight

    def getInfoBefore(self, db):
        self.__db_info = db.findNoEatenPlate(self.id)
        if not self.__db_info:
            return False
        return True

    def updateInfo(self, db):
        """
        将所有信息汇总成一个字典
        :return: 字典类型，所有成员变量
        """
        self.end_time = datetime.now().strftime('%H:%M')
        start_time = datetime.strptime(self.__db_info['start_time'], '%H:%M')
        self.meal_time = datetime.strptime(self.end_time, '%H:%M') - start_time
        plate = {
            "eaten": self.eaten,
            "rest_weight": self.rest_weight,
            "finish_time": self.end_time,
            "meal_time": str(self.meal_time)
        }
        db.updateNoEatenPlate(self.__db_info['plate_id'], plate)
        db.pushUpdateNoEatenPlate(self.__db_info['plate_id'], plate)

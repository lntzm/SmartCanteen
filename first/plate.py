from datetime import datetime


class Plate:
    def __init__(self):
        self.id = 0  # 盘子ID
        self.eaten = False  # 第一次，没有吃过
        self.name = ""  # 菜品名
        self.__db_info = {}

    def getID(self, baiduAPI, image_buffer) -> bool:
        """
        二维码识别获取盘子ID
        :param image: 输入图片
        :return 是否成功获取盘子ID
        """
        # detector = cv2.wechat_qrcode_WeChatQRCode("wechatQRCode/detect.prototxt",
        #                                           "wechatQRCode/detect.caffemodel",
        #                                           "wechatQRCode/sr.prototxt",
        #                                           "wechatQRCode/sr.caffemodel")
        # # 识别结果和位置
        # self.id, points = detector.detectAndDecode(image)
        self.id = baiduAPI.getNumberResult(image_buffer)
        if not self.id:
            return False
        else:
            return True

    def getName(self, baiduAPI, image_buffer) -> bool:
        """
        菜品识别获取菜品名与卡路里
        :param baiduAI: BaiduAPI类的一个对象，提供识别接口
        :param image: 输入图片
        """
        self.name, prob, _ = baiduAPI.getDishResult(image_buffer)
        if not self.name or float(prob) < 0.6:
            return False

        return True

    def searchDB(self, db):
        self.__db_info = db.findDish(self.name)

    def saveInfo(self, db):
        """
        将所有信息汇总成一个字典
        :return: 字典类型，所有成员变量
        """
        plate = {
            "_id": self.id,
            "eaten": self.eaten,
            "dish_name": self.name,
            "calories": self.__db_info['calories'],
            "fat": self.__db_info['fat'],
            "carbo": self.__db_info['carbo'],
            "protein": self.__db_info['protein'],
            "weight": self.__db_info['weight'],
            "price": self.__db_info['price'],
            "date": datetime.now().strftime('%Y-%m-%d'),
            "start_time": datetime.now().strftime('%H:%M')
        }
        db.addRecord(plate)

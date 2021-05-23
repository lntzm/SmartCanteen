import cv2


class Plate:
    def __init__(self, user: dict = None):
        self.id = 0  # 盘子ID
        self.eaten = False  # 第一次，没有吃过
        self.name = ""  # 菜品名
        self.calories = 0  # 菜品卡路里
        self.weight = 0  # 菜品重量
        self.price = 0  # 菜品价格

        if user is None:
            self.user = {}
        else:
            self.user = user  # 用户信息
            # 重命名user中的键id
            self.user["user_id"] = self.user.pop("_id")

    def getID(self, image) -> bool:
        """
        二维码识别获取盘子ID
        :param image: 输入图片
        :return 是否成功获取盘子ID
        """
        detector = cv2.wechat_qrcode_WeChatQRCode("wechatQRCode/detect.prototxt",
                                                  "wechatQRCode/detect.caffemodel",
                                                  "wechatQRCode/sr.prototxt",
                                                  "wechatQRCode/sr.caffemodel")
        # 识别结果和位置
        self.id, points = detector.detectAndDecode(image)
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
        self.name, prob, self.calories = baiduAPI.getDishResult(image_buffer)
        if not self.name or prob < 0.6:
            return False

        return True

    def getWeight(self):
        """
        查询数据库获取菜品重量
        :param
        :return:
        """
        pass

    def getPrice(self):
        """
        查询数据库获取菜品价格
        :param
        :return:
        """
        pass

    def matchUser(self, user: dict):
        self.user = user


    def saveInfo(self):
        """
        将所有信息汇总成一个字典
        :return: 字典类型，所有成员变量
        """
        plate = {
            "_id": self.id,
            "eaten": self.eaten,
            "dish_name": self.name,
            "calories": self.calories,
            "weight": self.weight,
            "price": self.price
        }
        plate.update(self.user)


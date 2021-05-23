import cv2
class Plate2nd:
    def __init__(self):
        self.id = 0             # 盘子ID
        self.eaten = True       # 第二次，已经吃过
        self.rest_weight = 0    # 剩余重量

    def getID(self, image):
        """
        二维码识别获取盘子ID
        :param baiduAI: BaiduAPI类的一个对象，提供识别接口
        :param image: 输入图片
        :return 是否成功获取盘子ID
        """
        detector = cv2.wechat_qrcode_WeChatQRCode("./detect.prototxt", "./detect.caffemodel", "./sr.prototxt",
                                                  "./sr.caffemodel")
        # 识别结果和位置
        res, points = detector.detectAndDecode(image)
        self.id = res
        if not self.id:
            print("> dish_id not found")
            return False
        else:
            print("> dish_id:", self.id)
        return True

    def getWeight(self, hx711):
        """
        称重获取剩余重量
        :param
        :return:
        """
        self.rest_weight = hx711.get_weight_mean(5)
        pass

    def getInfoBefore(self) -> bool:
        """
        查询数据库获取就餐取菜对应盘子信息
        :return:
        若未找到返回False
        """


    def saveInfo(self,db):
        """
        将所有信息汇总成一个字典
        :return: 字典类型，所有成员变量
        """
        plate = {"_id": self.id, "eaten": self.eaten, "rest_weight": self.rest_weight}  # 还可以继续添加一些信息，包括用餐时间等等
        db.addPlate(plate)



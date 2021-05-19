import cv2
class Plate1st:
    def __init__(self, dish: dict, user: dict):
        self.id = 0             # 盘子ID
        self.eaten = False      # 第一次，没有吃过
        self.dish = dish        # 菜品信息
        self.user = user        # 用户信息
        # 重命名dish和user中的键id
        self.dish["dish_id"] = self.dish.pop("_id")
        self.user["user_id"] = self.user.pop("_id")

    def getID(self, image) -> bool:
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

    def saveInfo(self):
        """
        保存数据到本地数据库
        """

    def sumInfo(self):
        """
        将所有信息汇总成一个字典
        :return: 字典类型，所有成员变量
        """
        plate = {
            "_id": self.id,
            "eaten": self.eaten
        }
        plate.update(self.dish)
        plate.update(self.user)
        return plate

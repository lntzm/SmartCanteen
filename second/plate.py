from datetime import datetime


class Plate:
    def __init__(self):
        self.id = 0  # 盘子ID
        self.eaten = True  # 第二次，已经吃过
        self.rest_weight = 0  # 剩余重量
        self.__db_info = None
        self.time2nd = ""  # 二次记录时间
        self.meal_time = 0  # 用餐时长

    def getID(self, baiduAPI, image_buffer):
        """
        二维码识别获取盘子ID
        :param baiduAI: BaiduAPI类的一个对象，提供识别接口
        :param image: 输入图片
        :return 是否成功获取盘子ID
        """
        self.id = baiduAPI.getNumberResult(image_buffer)
        if not self.id:
            return False
        return True

    def getWeight(self, hx711):
        """
        称重获取剩余重量
        :param
        :return:
        """
        weight = hx711.get_weight_mean(5)
        self.rest_weight = 0 if -10 < weight < 0 else weight

    # def searchDB(self, db):
    #     self.__db_info = db.findPlate(self.id)

    def getInfoBefore(self, db):
        self.__db_info = db.findNoEatenPlate(self.id)
        if not self.__db_info:
            return False
        return True

    def updateTime(self, time1st):
        self.time2nd = datetime.now().strftime('%Y-%m-%d %H:%M')
        self.meal_time = time1st - self.time2nd

    def updateInfo(self, db):
        """
        将所有信息汇总成一个字典
        :return: 字典类型，所有成员变量
        """
        self.time2nd = datetime.now().strftime('%Y-%m-%d %H:%M')
        self.meal_time = self.__db_info['start_time'] - self.time2nd
        plate = {
            "eaten": self.eaten,
            "rest_weight": self.rest_weight,
            "finish_time": self.time2nd,
            "meal_time": self.meal_time
        }
        db.updatePlate(plate)
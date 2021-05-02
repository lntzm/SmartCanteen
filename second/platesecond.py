class PlateSecond:
    def __init__(self):
        self.id = 0             # 盘子ID
        self.eaten = True       # 第二次，已经吃过
        self.rest_weight = 0    # 剩余重量

    def getID(self):
        """
        二维码识别获取盘子ID
        :param
        :return:
        """
        pass

    def getWeight(self):
        """
        称重获取剩余重量
        :param
        :return:
        """
        pass

    def getInfoBefore(self):
        """
        查询数据库获取就餐取菜对应盘子信息
        :return:
        """

    def sumInfo(self):
        """
        将所有信息汇总成一个字典
        :return: 字典类型，所有成员变量
        """
        return {
            "_id": self.id,
            "eaten": self.eaten,
            "rest_weight": self.rest_weight,
            # 还可以继续添加一些信息，包括用餐时间等等
        }


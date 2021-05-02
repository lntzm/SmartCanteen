class Dish:
    def __init__(self):
        self.name = ""      # 菜品名
        self.calories = 0   # 菜品卡路里
        self.weight = 0     # 菜品重量
        self.price = 0      # 菜品价格

    def getName(self):
        """
        菜品识别获取菜品名
        :param
        :return:
        """
        pass

    def getCalories(self):
        """
        菜品识别获取菜品卡路里
        :param
        :return:
        """
        pass

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

    def sumInfo(self) -> dict:
        """
        将需要记录到plates数据库的信息汇总成一个字典
        :return: 字典类型，有用的成员变量
        """
        return {
            "_id": self.name,
            "calories": self.calories,
            "weight": self.weight,
            "price": self.price
        }

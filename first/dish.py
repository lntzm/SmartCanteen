class Dish:
    def __init__(self):
        self.name = ""      # 菜品名
        self.calories = 0   # 菜品卡路里
        self.weight = 0     # 菜品重量
        self.price = 0      # 菜品价格

    def RecognizeDish(self, baiduAPI, image_buffer):
        """
        菜品识别获取菜品名与卡路里
        :param baiduAI: BaiduAPI类的一个对象，提供识别接口
        :param image: 输入图片
        """
        self.name, _, self.calories = baiduAPI.getDishResult(image_buffer)
        if not self.name:
            print("RecognizeDish false")
            return False
        else:
            print("> dish_name:", self.name)
            print("> dish_calories:", self.calories)
        return True


    def getWeight(self, db):
        """
        查询数据库获取菜品重量
        :param
        :return:
        """
        result = db.findDish(self.name)
        self.weight = result['weight']

    def getPrice(self, db):
        """
        查询数据库获取菜品价格
        :param
        :return:
        """
        result = db.findDish(self.name)
        self.price = result['price']


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

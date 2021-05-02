import pymongo


class Database:
    def __init__(self, db_host: str, db_name: str):
        client = pymongo.MongoClient(db_host)
        db = client[db_name]
        self.dishes_db = db["dishes"]
        self.users_db = db["users"]
        self.plates_db = db["plates"]

    def addDish(self, dish: dict):
        """
        往集合dishes添加记录
        :param dish: 字典类型，记录菜品信息
        :return: None
        """
        self.dishes_db.insert_one(dish)
        pass

    def addUser(self, user: dict):
        """
        往集合users添加记录
        :param user: 字典类型，记录用户信息
        :return: None
        """
        self.users_db.insert_one(user)
        pass

    def addPlate(self, plate: dict):
        """
        往集合plates添加记录
        :param plate: 字典类型，记录盘子信息
        :return:
        """
        self.plates_db.insert_one(plate)
        pass

    def findDish(self, dish_name: str):
        """
        根据dish_name查找菜品的相关信息
        :param dish_name: 字符串，菜品名
        :return: dish: 字典类型，返回这道菜的相关信息
        """
        pass

    def findUser(self, user_id: int):
        """
        根据user_id查找用户的相关信息
        :param user_id: 整数类型，用户唯一ID
        :return: user: 字典类型，返回该用户的相关信息
        """
        pass

    def findPlate(self, plate_id: int):
        """
        根据plate_id查找盘子的相关信息
        :param plate_id: 整数类型，盘子唯一ID
        :return: plate: 字典类型，返回该盘子的相关信息
        """
        pass

    def updateDish(self, dish_name: str, ):
        """
        根据dish_name查找菜品的相关信息
        :param dish_name: 字符串，菜品名
        :return: dish: 字典类型，返回这道菜的相关信息
        """
        pass

    def updateUser(self, user_id: int):
        """
        根据user_id查找用户的相关信息
        :param user_id: 整数类型，用户唯一ID
        :return: user: 字典类型，返回该用户的相关信息
        """
        pass

    def updatePlate(self, plate_id: int):
        """
        根据plate_id查找盘子的相关信息
        :param plate_id: 整数类型，盘子唯一ID
        :return: plate: 字典类型，返回该盘子的相关信息
        """
        pass


if __name__ == '__main__':
    db = Database("mongodb://localhost:27017/", "smartCanteen")
    pass

import pymongo

class Database:
    def __init__(self, db_host: str, db_name: str):
        client = pymongo.MongoClient(db_host)
        db = client[db_name]       #创建一个数据库
        self.dishes_db = db["dishes"]     #创建集合
        self.users_db = db["users"]
        self.plates_db = db["plates"]

    def addDish(self, dish: dict):
        """
        往集合dishes添加记录
        :param dish: 字典类型，记录菜品信息
        :return: None
        """
        self.dishes_db.insert_one(dish)


    def addUser(self, user: dict):
        """
        往集合users添加记录
        :param user: 字典类型，记录用户信息
        :return: None
        """
        self.users_db.insert_one(user)


    def addPlate(self, plate: dict):
        """
        往集合plates添加记录
        :param plate: 字典类型，记录盘子信息
        :return:
        """
        self.plates_db.insert_one(plate)

    def findDish(self, dish_name: str):
        result = self.dishes_db.find({'name': dish_name})
        """
        根据dish_name查找菜品的相关信息
        result = self.dishes_db.find({'name': dish_name},{"_id":0,"dish_name":1}) #只返回该菜品的名字,而_id是默认返回的
        find的第二键值用来返回所需要的字段信息
        :param dish_name: 字符串，菜品名
        :return: dish: 字典类型，返回这道菜的相关信息
        返回结果result是Cursor类型，相当于一个生成器，我们需要遍历取到所有的结果，每一个结果都是字典类型
        """
        return result

    def findUser(self, user_id: int):
        result = self.users_db.find({'name': user_id})
        """
        根据user_id查找用户的相关信息
        :param user_id: 整数类型，用户唯一ID
        :return: user: 字典类型，返回该用户的相关信息
        """
        return result

    def findPlate(self, plate_id: int):
        result = self.plates_db.find({'name': plate_id})
        """
        根据plate_id查找盘子的相关信息
        :param plate_id: 整数类型，盘子唯一ID
        :return: plate: 字典类型，返回该盘子的相关信息
        """
        return result

    def updateDish(self, name: str, change:dict):
        condition = {'user_id': name}
        self.dishes_db.update_one(condition, {'$set': change})

        """
        只更新一条
        """

    def updateUser(self, name: str, change: dict):
        condition = {'user_id': name}
        self.users_db.update_one(condition, {'$set': change})

        """
        只更新一条
        """

    def updatePlate(self, name: str, change: dict):
        condition = {'user_id': name}
        self.dishes_db.update_one(condition, {'$set': change})
        """
        只更新一条
        根据name查找盘子的相关信息,并且修改该盘子的信息，其中name变量是菜品的名字，key变量为键的名字，new变量为对应的更新的键的值
        :return: item: 字典类型，返回这个盘子的所有信息
        """

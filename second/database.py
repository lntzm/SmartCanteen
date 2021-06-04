import pymongo


class Database:
    def __init__(self, db_host: str, db_name: str):
        client = pymongo.MongoClient(db_host)
        db = client[db_name]  # 创建一个数据库
        self.dishes_db = db["dish"]  # 创建集合
        self.users_db = db["user"]
        self.plates_db = db["plate"]
        self.record = db["record"]
        self.test = db["test"]

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
        result = self.dishes_db.find_one({'_id': dish_name})
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
        result = self.users_db.find_one({'_id': user_id})
        """
        根据user_id查找用户的相关信息
        :param user_id: 整数类型，用户唯一ID
        :return: user: 字典类型，返回该用户的相关信息
        """
        return result

    def findPlate(self, plate_id: int):
        result = self.plates_db.find_one({'_id': plate_id})
        """
        根据plate_id查找盘子的相关信息
        :param plate_id: 整数类型，盘子唯一ID
        :return: plate: 字典类型，返回该盘子的相关信息
        """
        return result


    def updateDish(self, name: str, change: dict):
        condition = {'_id': name}
        self.dishes_db.update_one(condition, {'$set': change})

    def updateUser(self, user_id: str, change: dict):
        condition = {'_id': user_id}
        self.users_db.update_one(condition, {'$set': change})

    def updatePlate(self, dish_id: str, change: dict):
        condition = {'_id': dish_id}
        self.plates_db.update_one(condition, {'$set': change})

    def addRecord(self, plate: dict):
        self.record.insert_one(plate)

    def getRecord(self):
        return self.record.find()

    def mergeUserRecord(self, user: dict):
        self.plates_db.update_many({}, {'$set': user})

    def commitRecord(self):
        self.plates_db.insert(self.record.find())

    def pushRecord(self):
        pass

    def cleanRecord(self):
        self.record.delete_many()



if __name__ == '__main__':
    db = Database("mongodb://localhost:27017/", "SmartCanteen")
    db.test.update_many({}, {'$set': {"user_id": "yang dongjie"}})
    pass

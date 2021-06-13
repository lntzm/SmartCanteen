import pymongo
import requests
import json
import time


class Database:
    def __init__(self, db_host: str, db_name: str):
        client = pymongo.MongoClient(db_host)
        db = client[db_name]  # 创建一个数据库
        self.dishes_db = db["dish"]  # 创建集合
        self.users_db = db["user"]
        self.plates_db = db["plate"]
        self.record = db["record"]
        self.test = db["test"]
        self.db_cloud = DBCloud()

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

    def findUser(self, user_id: str):
        result = self.users_db.find_one({'_id': user_id})
        """
        根据user_id查找用户的相关信息
        :param user_id: 整数类型，用户唯一ID
        :return: user: 字典类型，返回该用户的相关信息
        """
        return result

    def findEatenPlate(self, plate_id: str):
        result = self.plates_db.find_one({'plate_id': plate_id,
                                          'eaten': True})
        """
        根据plate_id查找盘子的相关信息
        :param plate_id: 整数类型，盘子ID
        :return: plate: 字典类型，返回该盘子的相关信息
        """
        return result

    def findNoEatenPlate(self, plate_id: str):
        result = self.plates_db.find_one({'plate_id': plate_id,
                                          'eaten': False})
        return result

    def updateDish(self, name: str, change: dict):
        condition = {'_id': name}
        self.dishes_db.update_one(condition, {'$set': change})

    def updateUser(self, user_id: str, change: dict):
        condition = {'_id': user_id}
        self.users_db.update_one(condition, {'$set': change})

    def updatePlate(self, plate_id: str, change: dict):
        condition = {'plate_id': plate_id}
        self.plates_db.update_one(condition, {'$set': change})

    def updateNoEatenPlate(self, plate_id: str, change: dict):
        condition = {'plate_id': plate_id, 'eaten': False}
        self.plates_db.update_one(condition, {'$set': change})

    def pushUpdateNoEatenPlate(self, plate_id: str, change: dict):
        self.db_cloud.updateNoEatenPlate(plate_id, change)

    def addRecord(self, plate: dict):
        self.record.insert_one(plate)

    def findRecord(self, plate_id: str):
        return self.record.find_one({'plate_id': plate_id})

    def getRecord(self):
        return self.record.find()

    def mergeUserRecord(self, user: dict):
        self.record.update_many({}, {'$set': user})

    def commitRecord(self):
        self.plates_db.insert(self.record.find())

    def pushRecord(self):
        records = list(self.record.find())
        for record in records:
            record['_id'] = str(record['_id'])
            record['eaten'] = str(record['eaten'])
        self.db_cloud.addPlate(records)

    def syncDish(self):
        dishes = list(self.dishes_db.find())
        self.db_cloud.addDish(dishes)

    def syncUser(self, id: str, change: dict):
        self.db_cloud.updateUser(id, change)

    def cleanRecord(self):
        self.record.delete_many({})


class DBCloud:
    def __init__(self):
        self.WECHAT_URL = 'https://api.weixin.qq.com/'
        self.APP_ID = 'wx0d22019eaad3050c'
        self.APP_SECRET = 'a16cb285fca4fc4f7c710df712cc4a56'
        self.ENV = 'mydatabase1-4glgbmlu103a6c74'  # 云环境ID

    def get_access_token(self):
        url = '{0}cgi-bin/token?grant_type=client_credential&appid={1}&secret={2}'.format(self.WECHAT_URL, self.APP_ID,
                                                                                          self.APP_SECRET)
        response = requests.get(url)
        result = response.json()
        return result['access_token']

    def addUser(self, info: dict or list):
        accessToken = self.get_access_token()
        url = '{0}tcb/databaseadd?access_token={1}'.format(self.WECHAT_URL, accessToken)
        query = "db.collection('user').add({data:" + str(info) + "})"
        data = {
            "env": self.ENV,  # 云环境ID
            "query": query
        }
        response = requests.post(url, data=json.dumps(data))  # 用来观察数据增加是否成功
        if json.loads(response.text)['errcode'] != 0:  # 增加失败
            return False
        return True

    def addDish(self, info: dict or list):
        accessToken = self.get_access_token()
        url = '{0}tcb/databaseadd?access_token={1}'.format(self.WECHAT_URL, accessToken)
        query = "db.collection('dish').add({data:" + str(info) + "})"
        data = {
            "env": self.ENV,  # 云环境ID
            "query": query
        }
        response = requests.post(url, data=json.dumps(data))
        if json.loads(response.text)['errcode'] != 0:  # 增加失败
            return False
        return True

    def addPlate(self, info: dict or list):
        accessToken = self.get_access_token()
        url = '{0}tcb/databaseadd?access_token={1}'.format(self.WECHAT_URL, accessToken)
        query = "db.collection('plate').add({data:" + str(info) + "})"
        data = {
            "env": self.ENV,  # 云环境ID
            "query": query
        }
        response = requests.post(url, data=json.dumps(data))
        if json.loads(response.text)['errcode'] != 0:  # 增加失败
            return False
        return True

    def updateUser(self, name: str, change: dict):
        accessToken = self.get_access_token()
        url = '{0}tcb/databaseupdate?access_token={1}'.format(self.WECHAT_URL, accessToken)
        name_str = "'" + name + "'"
        collection = "db.collection('testlist').where({id:"
        text = "}).update({data:"
        query = collection + name_str + text + str(change) + "})"
        data = {
            "env": self.ENV,
            "query": query
        }
        response = requests.post(url, data=json.dumps(data))
        if json.loads(response.text)['errcode'] != 0:  # 更新失败
            return False
        return True

    def updatePlate(self, name: str, change: dict):
        accessToken = self.get_access_token()
        url = '{0}tcb/databaseupdate?access_token={1}'.format(self.WECHAT_URL, accessToken)
        name_str = "'" + name + "'"
        collection = "db.collection('plate').where({plate_id:"
        text = "}).update({data:"
        query = collection + name_str + text + str(change) + "})"
        # print(query)
        data = {
            "env": self.ENV,
            "query": query
        }
        response = requests.post(url, data=json.dumps(data))
        if json.loads(response.text)['errcode'] != 0:  # 更新失败
            return False
        return True

    def updateNoEatenPlate(self, name: str, change: dict):
        accessToken = self.get_access_token()
        url = '{0}tcb/databaseupdate?access_token={1}'.format(self.WECHAT_URL, accessToken)
        name_str = "'" + name + "'"
        collection = "db.collection('plate').where({eaten:'False', plate_id:"
        text = "}).update({data:"
        query = collection + name_str + text + str(change) + "})"
        data = {
            "env": self.ENV,
            "query": query
        }
        response = requests.post(url, data=json.dumps(data))
        if json.loads(response.text)['errcode'] != 0:  # 更新失败
            return False
        return True

    def updateDish(self, name: str, change: dict):
        accessToken = self.get_access_token()
        url = '{0}tcb/databaseupdate?access_token={1}'.format(self.WECHAT_URL, accessToken)
        name_str = "'" + name + "'"
        collection = "db.collection('dish').where({_id:"
        text = "}).update({data:"
        query = collection + name_str + text + str(change) + "})"
        # print(query)
        data = {
            "env": self.ENV,
            "query": query
        }
        response = requests.post(url, data=json.dumps(data))
        if json.loads(response.text)['errcode'] != 0:  # 更新失败
            return False
        return True


if __name__ == '__main__':
    db = Database("mongodb://localhost:27017/", "SmartCanteen")
    db.pushRecord()
    pass

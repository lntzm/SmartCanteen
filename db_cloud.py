import requests
import json
import time


class DB:
    def __init__(self):
        self.WECHAT_URL = 'https://api.weixin.qq.com/'
        self.APP_ID = 'wx0d22019eaad3050c'
        self.APP_SECRET = 'a16cb285fca4fc4f7c710df712cc4a56'
        self.ENV = 'mydatabase1-4glgbmlu103a6c74'  # 云环境ID
        self.accessToken = self.get_access_token()
        self.url = '{0}tcb/databaseadd?access_token={1}'.format(self.WECHAT_URL, self.accessToken)

    def get_access_token(self):
        url = '{0}cgi-bin/token?grant_type=client_credential&appid={1}&secret={2}'.format(self.WECHAT_URL, self.APP_ID,
                                                                                          self.APP_SECRET)
        response = requests.get(url)
        result = response.json()
        return result['access_token']

    def addUser(self, info: dict):
        query = "db.collection('users').add({data:" + str(info) + "})"
        data = {
            "env": self.ENV,  # 云环境ID
            "query": query
        }
        response = requests.post(self.url, data=json.dumps(data))  # 用来观察数据增加是否成功
        if json.loads(response.text)['errcode'] != 0:
            raise ValueError('增加失败')

    def addDish(self, info: dict):
        query = "db.collection('dishes').add({data:" + str(info) + "})"
        data = {
            "env": self.ENV,  # 云环境ID
            "query": query
        }
        response = requests.post(self.url, data=json.dumps(data))
        if json.loads(response.text)['errcode'] != 0:
            raise ValueError('增加失败')

    def addPlate(self, info: dict):
        query = "db.collection('plates').add({data:" + str(info) + "})"
        data = {
            "env": self.ENV,  # 云环境ID
            "query": query
        }
        response = requests.post(self.url, data=json.dumps(data))
        if json.loads(response.text)['errcode'] != 0:
            raise ValueError('增加失败')

    def updateUser(self, name: str, change: dict):
        name_str = "'" + name + "'"
        collection = "db.collection('users').where({_id:"
        text = "}).update({data:"
        query = collection + name_str + text + str(change) + "})"
        # print(query)
        data = {
            "env": self.ENV,
            "query": query
        }
        response = requests.post(self.url, data=json.dumps(data))
        if json.loads(response.text)['errcode'] != 0:
            raise ValueError('更新失败')

    def updatePlate(self, name: str, change: dict):
        name_str = "'" + name + "'"
        collection = "db.collection('plates').where({_id:"
        text = "}).update({data:"
        query = collection + name_str + text + str(change) + "})"
        # print(query)
        data = {
            "env": self.ENV,
            "query": query
        }
        response = requests.post(self.url, data=json.dumps(data))
        if json.loads(response.text)['errcode'] != 0:
            raise ValueError('更新失败')

    def updateDish(self, name: str, change: dict):
        name_str = "'" + name + "'"
        collection = "db.collection('dishes').where({_id:"
        text = "}).update({data:"
        query = collection + name_str + text + str(change) + "})"
        # print(query)
        data = {
            "env": self.ENV,
            "query": query
        }
        response = requests.post(self.url, data=json.dumps(data))
        if json.loads(response.text)['errcode'] != 0:
            raise ValueError('更新失败')

    # 查询某个集合中的数据，代码如下：
    """
    def query_data(self,accessToken,collection_name):
        url='{0}tcb/databasequery?access_token={1}'.format(self.WECHAT_URL,accessToken)
        query="db.collection('%s').limit(100).get()"%collection_name
        data={
            "env":self.ENV,
            "query":query
        }
        response  = requests.post(url,data=json.dumps(data))
        print('3.查询数据：'+response.text)
        result=response.json()
        print(result)
        # resultValue =json.loads(result)
        # return resultValue['_id']
    """
    """
    def db(self,):
        accessToken = self.get_access_token()
        print('accessToken:', accessToken)
        collectionName = 'test'
        # add_data(collectionName, accessToken)
        # query_data(accessToken, collectionName)
        self.databaseUpdate(accessToken, collectionName)
    """


# info = {'_id':'012','key':12,'value':'dick_ass','kj':404}
# db1 = DB()
# accessToken = db1.get_access_token()
# db1.databaseUpdate(accessToken,"canteen")

# start = time.time()
# db1.addUser(info)
# db1.updateUser("012", info)
# end = time.time()
# print(end-start)


if __name__ == '__main__':
    info = {'_id': '3333', 'key': 1, 'value': 'dick_asstest', 'kj': 4040}
    db1 = DB()

    start = time.time()
    db1.addUser(info)
    # db1.updateUser("3333", info)
    end = time.time()
    print(end - start)

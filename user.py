

class User:
    def __init__(self):
        self.id = 0         # 用户ID
        self.balance = 0    # 余额

    def getID(self):
        """
        人脸识别获取用户ID
        :param
        :return:
        """
        pass

    def getBalance(self):
        """
        查询数据库获取用户余额
        :param
        :return:
        """
        pass

    def sumInfo(self):
        """
        将需要记录到plates数据库的信息汇总成一个字典
        :return: 字典类型，有用的成员变量
        """
        return {
            "_id": self.id,
            "balance": self.balance
        }
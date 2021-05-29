from Face_RCN.FaceRCN import FaceRCN
import cv2


class User:
    def __init__(self):
        self.id = 0  # 用户ID
        self.balance = 0  # 余额
        self.__db_info = {}
        self.__faceRCN = FaceRCN()  # 人脸识别api

    def getID(self, img_rgb, group_id="test"):
        """
        人脸识别获取用户ID
        :param 1.RGB图片(numpy array类型) img_rgb
        :return: string类型 用户id
        """

        # 进行人脸搜索
        search_result = self.__faceRCN.face_search(img_rgb, group_id)
        if search_result is not None:  # 如果找到的话 返回用户id
            self.id = search_result['user_id']
            return True
        else:
            return False  # 没找到

    def searchDB(self, db):
        self.__db_info = db.findUser(self.id)

    def getBalance(self):
        """
        查询数据库获取用户余额
        :param
        :return:
        """
        self.balance = self.__db_info['balance']

    def sumInfo(self):
        """
        将需要记录到plates数据库的信息汇总成一个字典
        :return: 字典类型，有用的成员变量
        """
        return {
            "_id": self.id,
            "balance": self.balance
        }


if __name__ == '__main__':

    # 测试getID
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

    while cap.isOpened():
        ret, frame = cap.read()

        cv2.imshow('frame', frame)
        if cv2.waitKey(5) & 0xFF == 27:
            break

    cap.release()
    cv2.destroyAllWindows()

    user = User()
    # print(user.getID(frame))  # 打印搜索到的用户id

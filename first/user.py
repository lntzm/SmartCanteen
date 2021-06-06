from Face_RCN.FaceRCN import FaceRCN
import cv2


class User:
    def __init__(self):
        self.id = ""  # 用户ID
        self.balance = 0
        self.__faceRCN = FaceRCN()  # 人脸识别api

    def getID(self, img_rgb, group_id="test"):
        """
        人脸识别获取用户ID
        :param
            1. RGB图片img_rgb <numpy array>
            2. 人脸库分组 default="test" <string>
        :return: 用户id <string>
        """

        # 进行人脸搜索
        search_result = self.__faceRCN.face_search(img_rgb, group_id)
        # if search_result is not None:  # 如果找到的话 返回用户id
        #     return search_result['user_id']
        # else:
        #     return None  # 没找到
        if search_result is not None:  # 如果找到的话 返回用户id
            self.id = search_result['user_id']
            return True
        else:
            return False  # 没找到

    def saveInfo(self, db):
        """
        将需要记录到plates数据库的信息汇总成一个字典
        :return: 字典类型，有用的成员变量
        """
        db.mergeUserRecord({'user_id': self.id})

    def pay(self, db):
        self.balance = db.findUser(self.id)["balance"]
        prices = 0
        for plate in db.getRecord():
            prices += plate["price"]

        db.updateUser(self.id, {'balance': self.balance - prices})


if __name__ == '__main__':
        # 测试getID
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    frame = [None]

    while (cap.isOpened()):
        ret, f = cap.read()

        frame[0] = f
        cv2.imshow('frame', f)
        if cv2.waitKey(5) & 0xFF == 27:
            break

    cap.release()
    cv2.destroyAllWindows()

    user = User()
    print(user.getID(frame[0]))  # 打印搜索到的用户id

# if __name__ == '__main__':
#
#     # 测试getID
#     cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
#
#     while cap.isOpened():
#         ret, frame = cap.read()
#
#         cv2.imshow('frame', frame)
#         if cv2.waitKey(5) & 0xFF == 27:
#             break
#
#     cap.release()
#     cv2.destroyAllWindows()
#
#     user = User()
#     # print(user.getID(frame))  # 打印搜索到的用户id

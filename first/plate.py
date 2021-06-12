from datetime import datetime
import torch
from torchvision import transforms

from ImageHandle import b64DecodeCV
import cv2
from PIL import Image


class Plate:
    def __init__(self):
        self.id = 0  # 盘子ID
        self.eaten = False  # 第一次，没有吃过
        self.name = ""  # 菜品名
        self.__db_info = {}
        self.device = torch.device("cuda:0")
        self.model = torch.load('./dish/model/model.pkl')
        self.model.eval()
        self.transform = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.5, 0.5, 0.5],
                                 std=[0.5, 0.5, 0.5])
        ])
        self.dish_dict = {
            0: "土豆丝",
            1: "红烧肉",
            2: "米饭",
            3: "清蒸鱼",
            4: "油焖虾",
            5: "炒青菜",
            6: "番茄炒蛋",
            7: "红烧鸡腿",
            8: "红烧茄子",
            9: "炒花菜",
            10: "凉拌海带丝",
            11: "炒豆角"
        }
        self.QRCodeDetector = cv2.wechat_qrcode_WeChatQRCode("./wechatQRCode/detect.prototxt",
                                                             "./wechatQRCode/detect.caffemodel",
                                                             "./wechatQRCode/sr.prototxt",
                                                             "./wechatQRCode/sr.caffemodel")

    def getID(self, baiduAPI, img) -> bool:
        """
        二维码识别获取盘子ID
        :param image: 输入图片
        :return 是否成功获取盘子ID
        """
        # detector = cv2.wechat_qrcode_WeChatQRCode("wechatQRCode/detect.prototxt",
        #                                           "wechatQRCode/detect.caffemodel",
        #                                           "wechatQRCode/sr.prototxt",
        #                                           "wechatQRCode/sr.caffemodel")
        # # 识别结果和位置
        # self.id, points = detector.detectAndDecode(image)
        # self.id = baiduAPI.getNumberResult(img)
        res, _ = self.QRCodeDetector.detectAndDecode(img)
        if not res:
            return False
        self.id = res[0]
        return True

    def getName(self, image) -> bool:
        """
        菜品识别获取菜品名与卡路里
        :param image: 输入图片
        """
        # 使用ResNet18训练的模型进行预测
        image = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
        image = self.transform(image)
        image = image.view(1, 3, 224, 224)
        image = image.to(self.device)
        output = self.model(image)
        _, prediction = torch.max(output, 1)
        dish_key = prediction.tolist()[0]
        self.name = self.dish_dict[dish_key]
        return True

    def searchDB(self, db):
        self.__db_info = db.findDish(self.name)

    def saveInfo(self, db):
        """
        将所有信息汇总成一个字典
        :return: 字典类型，所有成员变量
        """
        plate = {
            "plate_id": self.id,
            "eaten": self.eaten,
            "dish_name": self.name,
            "calories": self.__db_info['calories'],
            "fat": self.__db_info['fat'],
            "carbo": self.__db_info['carbo'],
            "protein": self.__db_info['protein'],
            "weight": self.__db_info['weight'],
            "price": self.__db_info['price'],
            "date": datetime.now().strftime('%Y-%m-%d'),
            "start_time": datetime.now().strftime('%H:%M')
        }
        db.addRecord(plate)

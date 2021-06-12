import os
import time
import cv2
import torch
from torchvision import transforms
from PIL import Image


dish_dict = {
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
            11: "豆角炒肉"
        }


def predict(model, transform, img_path):
    model.eval()
    # image = Image.open(img_path)
    image = cv2.imread(img_path)
    image = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
    image = transform(image)
    image = image.view(1, 3, 224, 224)
    image = image.to(torch.device("cuda:0"))
    output = model(image)
    _, prediction = torch.max(output, 1)
    return dish_dict[prediction.tolist()[0]]


if __name__ == '__main__':
    test_root = './dish/data/test'
    device = torch.device("cuda:0")
    model = torch.load('./dish/model/model.pkl')
    # model.to(device)
    transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.5, 0.5, 0.5],
                             std=[0.5, 0.5, 0.5])
    ])
    start = time.time()
    for img_name in os.listdir(test_root):
        img_path = os.path.join(test_root, img_name)
        prediction = predict(model, transform, img_path)
        print(f"{img_name} 预测结果: {prediction}，用时{time.time() - start}")

import os
import time
import cv2
import torch
from torchvision import transforms
from PIL import Image

from dish.test import dish_dict


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
    test_root = './test'
    device = torch.device("cuda:0")
    model = torch.load('./dish/model/model.pkl')
    model_before = torch.load('./dish/bak/2nd/model.pkl')
    # model.to(device)
    transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.5, 0.5, 0.5],
                             std=[0.5, 0.5, 0.5])
    ])
    for situation in os.listdir(test_root):
        img_root = os.path.join(test_root, situation)
        if os.path.isfile(img_root):
            continue
        print(f"-----{situation}-----")
        for img_name in os.listdir(img_root):
            img_path = os.path.join(img_root, img_name)
            start = time.time()
            prediction = predict(model, transform, img_path)
            print(f"{img_name} 预测结果: {prediction}，用时{time.time() - start:.4f}")

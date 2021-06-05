import time

import torch
from torchvision import transforms
from PIL import Image


def predict(model, transform, img_path):
    model.eval()
    # image = Image.open(img_path)
    import cv2
    image = cv2.imread(img_path)
    image = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
    image = transform(image)
    image = image.view(1, 3, 224, 224)
    image = image.to(torch.device("cuda:0"))
    output = model(image)
    _, prediction = torch.max(output, 1)
    return prediction.tolist()[0]


if __name__ == '__main__':
    img_path = './dish/data/7/7_0.jpg'
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
    prediction = predict(model, transform, img_path)
    print(prediction)
    print(time.time() - start)


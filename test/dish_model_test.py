import cv2
import time
from ImageHandle import splitImg
import time

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
            11: "炒豆角"
        }

def predict(model, transform, image):
    model.eval()
    # image = Image.open(img_path)
    image = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
    image = transform(image)
    image = image.view(1, 3, 224, 224)
    image = image.to(torch.device("cuda:0"))
    output = model(image)
    _, prediction = torch.max(output, 1)
    return dish_dict[prediction.tolist()[0]]


if __name__ == '__main__':
    cap = cv2.VideoCapture(2)
    device = torch.device("cuda:0")
    model = torch.load('./dish/model/model.pkl')
    # model.to(device)
    transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.5, 0.5, 0.5],
                             std=[0.5, 0.5, 0.5])
    ])
    while True:
        ret, frame = cap.read()
        if not ret:
            print('No camera')
            continue
        # cv2.imshow('frame', frame)
        imgs,_ = splitImg(frame)
        img = imgs[0]
        # index = input("input index:")
        # cv2.imwrite("test.jpg", frame)
        # cv2.imshow('client', frame)
        start = time.time()
        prediction = predict(model, transform, img)
        print(f"预测结果: {prediction}，用时{time.time() - start}")
        cv2.imwrite('./test/弱光照/炒豆角.jpg', img)
        break

        # if count % 2:
        #     start = time.time()
        # else:
        #     print(time.time()-start)



        # cv2.imshow('client', frame)
        # count += 1


        # images, img_marked = splitImg(frame)
        # if not images:
        #     print("> plates not detected")
        #     continue
        #
        # for image in images:
        #     result = QRcode(image)
        #     print("图片返回结果为：", result)
        #
        # print("本次识别结束", len(images))
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

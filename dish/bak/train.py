import cv2
import pandas as pd
import numpy as np
import paddle
import paddle.vision.transforms as T

from paddle.io import Dataset
from paddle.metric import Accuracy
from paddle.vision.models import resnet18

# import warnings
# warnings.filterwarnings("ignore")


class MyDataset(Dataset):
    """
    步骤一：继承paddle.io.Dataset类
    """

    def __init__(self, img_path_list, label_list, transform):
        """
        步骤二：实现构造函数，定义数据集大小
        """
        super(MyDataset, self).__init__()

        self.img_path_list = img_path_list
        self.label_list = label_list
        self.transform = transform

    def __getitem__(self, index):
        """
        步骤三：实现__getitem__方法，定义指定index时如何获取数据，并返回单条数据（训练数据，对应的标签）
        """
        img = cv2.imread(self.img_path_list[index])
        img = self.transform(img)
        img = np.ndarray(img)
        label = np.ndarray([self.label_list[index]]).astype(dtype='int64')

        return img, label

    def __len__(self):
        """
        步骤四：实现__len__方法，返回数据集总数目
        """
        return len(self.img_path_list)


transform = T.Compose([
    T.Resize([224, 224]),
    # T.ToTensor(),
    T.Normalize(mean=[0.5, 0.5, 0.5], std=[0.5, 0.5, 0.5])
])

# 读取数据
df = pd.read_csv('./dish/data/dataset.csv')
image_path_list = df['images'].values
label_list = df['labels'].values

# 划分训练集和校验集
all_size = len(image_path_list)
train_size = int(all_size * 0.8)
train_image_path_list = image_path_list[:train_size]
train_label_list = label_list[:train_size]
val_image_path_list = image_path_list[train_size:]
val_label_list = label_list[train_size:]

train_dataset = MyDataset(train_image_path_list, train_label_list, transform=transform)
val_dataset = MyDataset(val_image_path_list, val_label_list, transform=transform)
# train_loader = paddle.io.DataLoader(train_dataset, batch_size=8, shuffle=True)

# build model
model = resnet18(pretrained=True, num_classes=10, with_pool=True)

# 调用飞桨框架的VisualDL模块，保存信息到目录中。
callback = paddle.callbacks.VisualDL(log_dir='./dish/model/')

# # 自定义Callback 记录训练过程中的loss信息
# class LossCallback(paddle.callbacks.Callback):
#
#     def on_train_begin(self, logs={}):
#         # 在fit前 初始化losses，用于保存每个batch的loss结果
#         self.losses = []
#         self.acc = []
#
#     def on_train_batch_end(self, step, logs={}):
#         # 每个batch训练完成后调用，把当前loss添加到losses中
#         self.losses.append(logs.get('loss'))
#         self.acc.append(logs.get('acc_top1'))
#
#
# # 初始化一个loss_log 的实例，然后将其作为参数传递给fit
# loss_log = LossCallback()

model = paddle.Model(model)
optim = paddle.optimizer.Adam(learning_rate=0.001, parameters=model.parameters())

# 配置模型
model.prepare(
    optim,
    paddle.nn.CrossEntropyLoss(),
    Accuracy(topk=(1, 2))
)

model.fit(train_dataset,
          epochs=10,
          batch_size=8,
          verbose=1,
          callbacks=callback
          )

model.evaluate(val_dataset, batch_size=8, verbose=1)

model.save('./dish/inference_model', False)

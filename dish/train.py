import copy
import time
import torch
import torch.nn as nn
import torch.optim as optim
import pandas as pd
# from skimage import io
from PIL import Image
from torch.utils.data import Dataset, DataLoader
from torchvision import models, transforms
import matplotlib.pyplot as plt


class MyDataset(Dataset):
    def __init__(self, csv_df, transform=None):
        self.df = csv_df
        self.transform = transform

    def __len__(self):
        return len(self.df)

    def __getitem__(self, idx):
        if torch.is_tensor(idx):
            idx = idx.tolist()
        # image = io.imread(self.df.iloc[idx, 0])
        image = Image.open(self.df.iloc[idx, 0])
        label = self.df.iloc[idx, 1]

        if self.transform:
            image = self.transform(image)

        label = torch.tensor(label)
        return image, label


def my_resnet18(num_classes):
    model = models.resnet18(pretrained=True)
    num_ftrs = model.fc.in_features
    model.fc = nn.Linear(num_ftrs, num_classes)
    return model


def my_resnet34(num_classes):
    model = models.resnet34(pretrained=True)
    num_ftrs = model.fc.in_features
    model.fc = nn.Linear(num_ftrs, num_classes)
    return model

def train_model(num_epochs=25):
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=0.001)
    scheduler = optim.lr_scheduler.StepLR(optimizer, step_size=7, gamma=0.1)

    since = time.time()

    best_model_wts = copy.deepcopy(model.state_dict())
    best_acc = 0.0

    for epoch in range(num_epochs):
        print('Epoch {}/{}'.format(epoch, num_epochs - 1))
        print('-' * 10)

        train(criterion, optimizer, scheduler)
        epoch_acc = validate(criterion, optimizer)

        # deep copy the model
        if epoch_acc > best_acc:
            best_acc = epoch_acc
            best_model_wts = copy.deepcopy(model.state_dict())

        checkpoint = {"model_state_dict": model.state_dict(),
                      "optimizer_state_dict": optimizer.state_dict(),
                      "best_model_wts": best_model_wts,
                      "epoch": epoch}
        torch.save(checkpoint, f'./dish/model/checkpoint/checkpoint_epoch{epoch}.pkl')
        print()

    time_elapsed = time.time() - since
    print('Training complete in {:.0f}m {:.0f}s'.format(
        time_elapsed // 60, time_elapsed % 60))
    print('Best val Acc: {:4f}'.format(best_acc))

    # load best model weights
    model.load_state_dict(best_model_wts)
    return model


def train(criterion, optimizer, scheduler):
    model.train()  # Set model to training mode

    running_loss = 0.0
    running_corrects = 0

    # Iterate over data.
    for inputs, labels in train_dataloader:
        inputs = inputs.to(device)
        labels = labels.to(device)

        # zero the parameter gradients
        optimizer.zero_grad()

        # forward
        # track history if only in train
        with torch.set_grad_enabled(True):
            outputs = model(inputs)
            _, preds = torch.max(outputs, 1)
            loss = criterion(outputs, labels)

            # backward + optimize only if in training phase
            loss.backward()
            optimizer.step()

        # statistics
        running_loss += loss.item() * inputs.size(0)
        running_corrects += torch.sum(preds == labels.data)
    scheduler.step()

    epoch_loss = running_loss / len(train_dataset)
    epoch_acc = running_corrects.double() / len(train_dataset)

    print('train loss: {:.4f} acc: {:.4f}'.format(epoch_loss, epoch_acc))


def validate(criterion, optimizer):
    model.eval()  # Set model to evaluate mode

    running_loss = 0.0
    running_corrects = 0

    # Iterate over data.
    for inputs, labels in val_dataloader:
        inputs = inputs.to(device)
        labels = labels.to(device)

        # zero the parameter gradients
        optimizer.zero_grad()

        # forward
        # track history if only in train
        with torch.no_grad():
            outputs = model(inputs)
            _, preds = torch.max(outputs, 1)
            loss = criterion(outputs, labels)

        # statistics
        running_loss += loss.item() * inputs.size(0)
        running_corrects += torch.sum(preds == labels.data)

    epoch_loss = running_loss / len(val_dataset)
    epoch_acc = running_corrects.double() / len(val_dataset)

    print('val loss: {:.4f} acc: {:.4f}'.format(epoch_loss, epoch_acc))
    return epoch_acc


# def visualize_model(num_images=6):
#     was_training = model.training
#     model.eval()
#     images_so_far = 0
#     fig = plt.figure()
#
#     with torch.no_grad():
#         for i, (inputs, labels) in enumerate(val_dataloader):
#             inputs = inputs.to(device)
#             labels = labels.to(device)
#
#             outputs = model(inputs)
#             _, preds = torch.max(outputs, 1)
#
#             for j in range(inputs.size()[0]):
#                 images_so_far += 1
#                 ax = plt.subplot(num_images//2, 2, images_so_far)
#                 ax.axis('off')
#                 ax.set_title('predicted: {}'.format(preds[j]))
#                 plt.imshow(inputs.cpu().data[j])
#
#                 if images_so_far == num_images:
#                     model.train(mode=was_training)
#                     return
#         model.train(mode=was_training)


if __name__ == '__main__':
    transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.5, 0.5, 0.5],
                             std=[0.5, 0.5, 0.5])
    ])
    data_df = pd.read_csv('./dish/data/dataset.csv')
    train_df = data_df.sample(frac=0.8)
    train_dataset = MyDataset(train_df, transform)
    train_dataloader = DataLoader(train_dataset, batch_size=8, num_workers=4)

    val_df = data_df[~data_df.index.isin(train_df.index)]
    val_dataset = MyDataset(val_df, transform)
    val_dataloader = DataLoader(val_dataset, batch_size=8, num_workers=4)

    device = torch.device("cuda:0")
    model = my_resnet18(num_classes=13)
    model.to(device)

    model = train_model(num_epochs=6)

    torch.save(model, './dish/model/model.pkl')

    # visualize_model(num_images=6)
    # plt.ioff()
    # plt.show()

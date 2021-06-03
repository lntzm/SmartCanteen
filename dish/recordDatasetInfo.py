import pandas as pd
import numpy as np
import os


def generateList(pic_root):
    classes = [c for c in os.listdir(pic_root) if os.path.isdir(os.path.join(pic_root, c))]

    img_list = []
    label_list = []

    for class_name in classes:
        class_path = os.path.join(pic_root, class_name)

        for i, img_name in enumerate(os.listdir(class_path)):
            img_path = os.path.join(class_path, img_name)
            img_list.append(img_path)
            label_list.append(int(class_name)-1)

    return img_list, label_list


def write2csv(img_list, label_list, pic_root):
    img_df = pd.DataFrame(img_list)
    label_df = pd.DataFrame(label_list)

    img_df.columns = ['images']
    label_df.columns = ['labels']

    df = pd.concat([img_df, label_df], axis=1)
    df = df.reindex(np.random.permutation(df.index))
    df.to_csv(os.path.join(pic_root, 'dataset.csv'), index=0)


if __name__ == '__main__':
    pic_root = './dish/data'
    img_list, label_list = generateList(pic_root)
    write2csv(img_list, label_list, pic_root)

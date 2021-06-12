import os
from PIL import Image, ImageEnhance
import Augmentor


def rotateImage(img_path):
    img = Image.open(img_path)
    angles = [15 * i for i in range(1, 24)]
    for angle in angles:
        img_rotated = img.rotate(angle)
        new_path = os.path.splitext(img_path)[0] + f"_rotate{angle}" + os.path.splitext(img_path)[1]
        img_rotated.save(new_path)


def adjustBrightColorContrastSharp(img_path):
    img = Image.open(img_path)
    brightness = [0.6, 0.75, 0.9, 1.1, 1.25, 1.4]
    color = [0.7, 0.8, 0.9, 1.1, 1.2, 1.3]
    contrast = [0.7, 0.8, 0.9, 1.1, 1.2, 1.3]
    sharpness = [0.7, 0.8, 0.9, 1.1, 1.2, 1.3]
    for i in brightness:
        img_new = ImageEnhance.Brightness(img).enhance(i)
        new_path = os.path.splitext(img_path)[0] + f"_brightness{i}" + os.path.splitext(img_path)[1]
        img_new.save(new_path)
    for i in color:
        img_new = ImageEnhance.Color(img).enhance(i)
        new_path = os.path.splitext(img_path)[0] + f"_color{i}" + os.path.splitext(img_path)[1]
        img_new.save(new_path)
    for i in contrast:
        img_new = ImageEnhance.Contrast(img).enhance(i)
        new_path = os.path.splitext(img_path)[0] + f"_contrast{i}" + os.path.splitext(img_path)[1]
        img_new.save(new_path)
    for i in sharpness:
        img_new = ImageEnhance.Sharpness(img).enhance(i)
        new_path = os.path.splitext(img_path)[0] + f"_sharpness{i}" + os.path.splitext(img_path)[1]
        img_new.save(new_path)


def adjustDistortion(class_path):
    p = Augmentor.Pipeline(class_path)
    p.random_distortion(probability=1, grid_width=2, grid_height=2, magnitude=4)
    p.sample(96)
    p.random_distortion(probability=1, grid_width=3, grid_height=3, magnitude=5)
    p.sample(96)


if __name__ == '__main__':
    pic_root = './dish/data'
    classes = [c for c in os.listdir(pic_root) if os.path.isdir(os.path.join(pic_root, c))]

    for class_name in classes:
        class_path = os.path.join(pic_root, class_name)
        for img_name in os.listdir(class_path):
            if not img_name.endswith('.jpg'):
                continue
            img_path = os.path.join(class_path, img_name)
            rotateImage(img_path)
            adjustBrightColorContrastSharp(img_path)
        # adjustDistortion(class_path)


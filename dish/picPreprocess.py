import cv2
import numpy as np
import os
from PIL import Image
import piexif


def png2jpg(png_path):
    if os.path.splitext(png_path)[-1] != '.png':
        print(f"\t> {png_path} is not a png file, skip")
        return
    img = Image.open(png_path)
    if len(img.split()) == 4:

        white = Image.new("RGBA", img.size, color=(255, 255, 255, 255))
        img = Image.alpha_composite(white, img)

        R, G, B, A = img.split()
        img = Image.merge("RGB", (R, G, B)).convert('RGB')
    else:
        img = img.convert('RGB')
    jpg_path = os.path.splitext(png_path)[0] + '.jpg'
    img.save(jpg_path, quality=100)
    os.remove(png_path)
    print("\t> changed {} to {}".format(os.path.basename(png_path),
                                        os.path.basename(jpg_path)))
    return jpg_path


def checkImage(img_path):
    try:
        pil_im = Image.open(img_path)
        pil_im.load()
    except:
        print("\t> cannot open {}, deleting...".format(img_path))
        # os.remove(img_path)
        return

    try:
        piexif.remove(img_path)
    except:
        print("\t> cannot remove EXIF info of {}, deleting...".format(img_path))
        # os.remove(img_path)
        # os.system("mv '{}' '/home/lzh/Desktop/temp'".format(img_path))
        return

    saving_flag = False
    if pil_im.mode != "RGB":
        pil_im = pil_im.convert("RGB")
        saving_flag = True
        print("\t> convert {} to RGB".format(img_path))

    im = np.array(pil_im)
    if len(im.shape) < 2:
        im = im[0]
        pil_im = Image.fromarray(im)
        pil_im.save(os.path.splitext(img_path)[0] + '.jpg', quality=100)
        print("\t> too few channels: {}".format(img_path))
    elif len(im.shape) == 3 and im.shape[2] >= 4:
        im = im[:, :, :3]
        pil_im = Image.fromarray(im)
        pil_im.save(os.path.splitext(img_path)[0] + '.jpg', quality=100)
        print("\t> too many channels: {}".format(img_path))
    else:
        if saving_flag:
            pil_im.save(os.path.splitext(img_path)[0] + '.jpg', quality=100)


def renameImage(class_name, class_path, img_name, index):
    name = f"{class_name}_{index}" + os.path.splitext(img_path)[-1]
    os.rename(os.path.join(class_path, img_name), os.path.join(class_path, name))


if __name__ == '__main__':
    pic_root = './dish/data'
    classes = [c for c in os.listdir(pic_root) if os.path.isdir(os.path.join(pic_root, c))]

    for class_name in classes:
        class_path = os.path.join(pic_root, class_name)

        for i, img_name in enumerate(os.listdir(class_path)):
            img_path = os.path.join(class_path, img_name)
            # png2jpg(img_path)
            # checkImage(img_path)
            renameImage(class_name, class_path, img_name, i)


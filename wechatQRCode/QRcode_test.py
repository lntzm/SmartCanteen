import cv2
from ImageHandle import *
from baiduAPI import BaiduAPI
from PIL import Image, ImageEnhance
import time


def QRcode(img):
    detector = cv2.wechat_qrcode_WeChatQRCode("./wechatQRCode/detect.prototxt",
                                              "./wechatQRCode/detect.caffemodel",
                                              "./wechatQRCode/sr.prototxt",
                                              "./wechatQRCode/sr.caffemodel")
    # 识别结果和位置
    res, points = detector.detectAndDecode(img)
    return res


def bright_enhance(img):
    for b in range(5):
        bright_enhancer = ImageEnhance.Brightness(img)
        bright_img_up = bright_enhancer.enhance(1 - 0.05 * j)
        temp = QRcode(bright_img_up)
        if temp:
            return temp

        bright_img_down = bright_enhancer.enhance(1 + 0.05 * j)
        temp = QRcode(bright_img_down)
        if temp:
            return temp
        return False


def contrast_enhance(img):
    for c in range(5):
        contrast_enhancer = ImageEnhance.Contrast(img)
        contrast_img_up = contrast_enhancer.enhance(1 - 0.05 * j)
        temp = QRcode(contrast_img_up)
        if temp:
            return temp
        contrast_img_down = contrast_enhancer.enhance(1 + 0.05 * j)
        temp = QRcode(contrast_img_down)
        if temp:
            return temp
        return False


def sort_image(images, locs):
    locs_array = np.array([locs[i][0] for i in range(len(locs))])
    locs_sorts = np.sort(locs_array)
    images_sort = []
    for loc in locs_array:
        images_sort.append(np.where(locs_sorts == loc)[0][0])

    images_sort = [images[i] for i in images_sort]

    return images_sort


if __name__ == '__main__':
    cap = cv2.VideoCapture(1)
    baiduAPI = BaiduAPI()
    # index = [False, False, False]
    result = [None, None, None]
    # result = ['', '', '']
    count = 0
    fail = 0
    bright = 0
    contrast = 0
    while True:
        ret, frame = cap.read()
        if not ret:
            print('No camera')
            continue

        cv2.imshow('client', frame)
        images, locs = splitImg(frame)
        images = sort_image(images, locs)

        if not images:
            print("> plates not detected")
            continue
        print("分割到", len(images), "个区域")

        for i, image in enumerate(images):
            if result[i]:
                continue
            result[i] = QRcode(image)

        for i, image in enumerate(images):
            # 微信识别
            temp = QRcode(image)
            if temp and index[i] == False:
                index[i] = True
                result[i] = temp
        count += 1
        if False in index and count != 10:
            continue

        for j, image in enumerate(images):
            if index[j]:
                print("> plate_ID:", result[j])
            else:
                print(">  10times failed to recognize the picture", j)
                img = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGRA2RGBA))
                bright_img = bright_enhance(img)
                if bright_img:
                    bright += 1
                    print(">  bright_enhance success", bright)

                    result[j] = bright_img
                    contrast_img = contrast_enhance(img)
                elif contrast_img:
                    contrast += 1
                    print(">  contrast_enhance success", contrast)

                    result = contrast_img
                else:
                    print(">  the enhancement failed")
                    fail += 1
                    print(">  fail times:", fail)

            # print(result[j])

            # # 百度API识别
            # image_buffer = CVEncodeb64(image)
            # result = baiduAPI.getNumberResult(image_buffer)

            # for i in range(10):
            #     result = QRcode(image)
            #     if (not result) and i != 9:
            #         continue
            #     elif i == 9:
            #         print("<  fail to recognize plate_ID")
            #     else:
            #         print("<  plate_ID:", result)
            #         break
            # continue

        # time.sleep(1)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

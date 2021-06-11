from hx711 import HX711
import cv2
import RPi.GPIO as GPIO
from datetime import datetime

if __name__ == '__main__':
    GPIO.setmode(GPIO.BCM)
    hx1 = HX711(dout_pin=21, pd_sck_pin=20, offset=153430, ratio=424.79)
    hx2 = HX711(dout_pin=26, pd_sck_pin=19, offset=1451, ratio=430.58)
    hx3 = HX711(dout_pin=6, pd_sck_pin=5, offset=74428, ratio=432.34)

    # hx1.correct_offset_ratio()
    # hx2.correct_offset_ratio()
    # hx3.correct_offset_ratio()
    while True:
        hx1_weight = hx1.get_weight_mean(8)
        # hx2_weight = hx2.get_weight_mean(10)
        # hx3_weight = hx3.get_weight_mean(10)
        # print(hx1_weight, hx2_weight, hx3_weight)
        print("检测到1号盘子，重量为：", hx1_weight)
        # print("检测到2号盘子，重量为：", hx2_weight)
        # print("检测到3号盘子，重量为：", hx3_weight)

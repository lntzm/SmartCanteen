# !/usr/bin/python3
# -*- coding: utf-8 -*-
import RPi.GPIO as GPIO  # 导入Rpi.GPIO库函数命名为GPIO
import time  # 导入计时time函数
import socket
import cv2


def recieve(index):
    
    if index:
        GPIO.output(switchOut, GPIO.HIGH)
        print("关锁")
    else:
        GPIO.output(switchOut, GPIO.LOW)
        print("开锁")



if __name__ == '__main__':
    # GPIO port
    # switchIn = 36
    switchOut = 18
    # flowSensor = 12
    # light = 32

    GPIO.setmode(GPIO.BOARD)  # 将GPIO编程方式设置为BOARD模式
    GPIO.setup(switchOut, GPIO.OUT)
    # GPIO.setup(flowSensor, GPIO.IN)
    while True:
        try:
            index = eval(input())
            recieve(index)
        except (KeyboardInterrupt, SystemExit):
            GPIO.cleanup()
            break


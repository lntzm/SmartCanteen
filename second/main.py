from plate2nd import Plate2nd
# from database import Database

from HX711 import HX711
import RPi.GPIO as GPIO
import time


if __name__ == '__main__':
    GPIO.setmode(GPIO.BCM)
    hx1 = HX711(dout_pin=21, pd_sck_pin=20, offset=31099, ratio=428.544)
    try:
        pass

    finally:
        GPIO.cleanup()
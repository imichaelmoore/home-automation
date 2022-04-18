""" Uses Raspberry Pi GPIO-attached Ultrasonic sensor to measure water level in cistern tank """
import sys
import RPi.GPIO as GPIO
import time
from statistics import mean
import time
import datetime
import sqlite3
from pprint import pprint
from math import floor

GPIO.setmode(GPIO.BCM)

GPIO_TRIGGER = 3
GPIO_ECHO = 2

GPIO.setup(GPIO_TRIGGER, GPIO.OUT)
GPIO.setup(GPIO_ECHO, GPIO.IN)

def distance():
    # set Trigger to HIGH
    GPIO.output(GPIO_TRIGGER, True)

    # set Trigger after 0.01ms to LOW
    time.sleep(0.00001)
    GPIO.output(GPIO_TRIGGER, False)

    StartTime = time.time()
    StopTime = time.time()

    # save StartTime
    while GPIO.input(GPIO_ECHO) == 0:
        StartTime = time.time()

    # save time of arrival
    while GPIO.input(GPIO_ECHO) == 1:
        StopTime = time.time()

    # time difference between start and arrival
    TimeElapsed = StopTime - StartTime
    # multiply with the sonic speed (34300 cm/s)
    # and divide by 2, because there and back
    distance_from_sensor = (TimeElapsed * 34300) / 2
    total=183
    percent = floor((183-distance_from_sensor) / 183 * 100)
    return percent, distance_from_sensor

print(distance())

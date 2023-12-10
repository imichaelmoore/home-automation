""" 
Uses Raspberry Pi GPIO-attached Ultrasonic sensor to measure water level in a cistern tank.
"""

import time
import RPi.GPIO as GPIO
from math import floor
from collections import namedtuple

# GPIO Pins setup
GPIO_TRIGGER = 3
GPIO_ECHO = 2

# GPIO Mode (BOARD / BCM)
GPIO.setmode(GPIO.BCM)

# Set GPIO direction (IN / OUT)
GPIO.setup(GPIO_TRIGGER, GPIO.OUT)
GPIO.setup(GPIO_ECHO, GPIO.IN)

# Namedtuple for storing measurement results
Measurement = namedtuple("Measurement", ["percent_full", "distance_cm"])


def measure_distance() -> Measurement:
    """
    Measures the distance using ultrasonic sensor.

    Returns:
        Measurement: A namedtuple containing the percentage of water in the tank and the distance measured by the sensor.
    """
    # Set Trigger to HIGH
    GPIO.output(GPIO_TRIGGER, True)

    # Set Trigger after 0.01ms to LOW
    time.sleep(0.00001)
    GPIO.output(GPIO_TRIGGER, False)

    start_time = time.time()
    stop_time = time.time()

    # Save start time
    while GPIO.input(GPIO_ECHO) == 0:
        start_time = time.time()

    # Save time of arrival
    while GPIO.input(GPIO_ECHO) == 1:
        stop_time = time.time()

    # Calculate time difference between start and arrival
    time_elapsed = stop_time - start_time

    # Sonic speed (34300 cm/s), divide by 2 for the round trip
    distance_from_sensor = (time_elapsed * 34300) / 2

    # Tank height in cm (example: 183 cm)
    total_height = 183

    # Calculate the percentage of water in the tank
    percent_full = floor((total_height - distance_from_sensor) / total_height * 100)

    return Measurement(percent_full, distance_from_sensor)


def main():
    try:
        measurement = measure_distance()
        print(f"Water level: {measurement.percent_full}%")
        print(f"Distance from sensor: {measurement.distance_cm} cm")
    except KeyboardInterrupt:
        print("Measurement stopped by User")
        GPIO.cleanup()


if __name__ == "__main__":
    main()

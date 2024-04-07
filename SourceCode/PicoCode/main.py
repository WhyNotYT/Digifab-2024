"""
A simple example that sweeps a Servo back-and-forth
Requires the micropython-servo library - https://pypi.org/project/micropython-servo/
"""

import time
from machine import Pin
import sys
import machine
import time
from servo import Servo

# Create our Servo object, assigning the
# GPIO pin connected the PWM wire of the servo
my_servo = Servo(pin_id=16)
buzzer = Pin("GP17", machine.Pin.OUT)
delay_ms = 25  # Amount of milliseconds to wait between servo movements

while True:
    v = sys.stdin.readline().strip()

    if v.lower() == "on":
        print("Turned on!")
        my_servo.write(180)
        buzzer.value(1)
        time.sleep(1)

    buzzer.value(0)
    my_servo.write(0)

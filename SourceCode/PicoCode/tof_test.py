from machine import I2C
from vl53l1x import VL53L1X
import time
import machine

i2c = I2C(id=0, sda=machine.Pin("GP4"), scl=machine.Pin("GP5"), freq=400000)

print(i2c.scan())
distance = VL53L1X(i2c)

while True:
    print("range: mm ", distance.read())
    time.sleep_ms(50)

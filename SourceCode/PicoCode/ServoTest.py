import servo
import time

pointing_servo = servo.Servo(pin_id="GP7")


while True:
    pointing_servo.write(25)
    time.sleep(1)
    pointing_servo.write(165)
    time.sleep(1)

# Test code for the Wwokwi.com basic circuit
# https://wokwi.com/projects/394594113656475649

from picozero import Speaker #Buzzer
from machine import Pin # Pins
from picozero import Servo  # importing Servo class to easily control the servo motor
from time import sleep

# creating a Speaker, led and servo object
speaker = Speaker(1)
led = Pin(2, Pin.OUT)
servo = Servo(15)
switch = Pin(28, Pin.IN)

# continuously beep at 1 sec interval while the board has power
# Test code will also turn led on/off with buzzer and turn servo motor between full and zero position 
# note: a passive buzzer can also be used to play different tones
while True:
    if switch.value() == 1:
        speaker.on()
        led.toggle()
        servo.value = 1
        sleep(1)
        speaker.off()
        led.toggle()
        servo.value = 0
        sleep(1)
    else:
       sleep(1) 
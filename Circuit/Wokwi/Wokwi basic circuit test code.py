# Basic circuit plan for the peili project: On/Off switch, buzzer, signal led, servo motor and Pi Pico W with test code
# Code for playing music with buzzer is from https://www.tomshardware.com/how-to/buzzer-music-raspberry-pi-pico
# Example code is for 180 degree servo, you need different code for continous rotation servo
# https://github.com/TTitanUA/micropython_servo_pdm_360 might work
# TODO: Check if the micro servo needs logic level shifter to work (5V->3.3V)
# Resistor on buzzer might not be necessary

#from picozero import Speaker #If using buzzer for just on/off sound
from machine import Pin, PWM # Pins, PWM control for buzzer
from picozero import Servo  # importing Servo class to  control the servo motor
from time import sleep

# creating a Speaker, led and servo object
buzzer = PWM(Pin(1))
#speaker = Speaker(1)
led = Pin(2, Pin.OUT)
servo = Servo(15)
switch = Pin(28, Pin.IN)

# Dictionary for matching tones with frequency
tones = {
"B0": 31,
"C1": 33,
"CS1": 35,
"D1": 37,
"DS1": 39,
"E1": 41,
"F1": 44,
"FS1": 46,
"G1": 49,
"GS1": 52,
"A1": 55,
"AS1": 58,
"B1": 62,
"C2": 65,
"CS2": 69,
"D2": 73,
"DS2": 78,
"E2": 82,
"F2": 87,
"FS2": 93,
"G2": 98,
"GS2": 104,
"A2": 110,
"AS2": 117,
"B2": 123,
"C3": 131,
"CS3": 139,
"D3": 147,
"DS3": 156,
"E3": 165,
"F3": 175,
"FS3": 185,
"G3": 196,
"GS3": 208,
"A3": 220,
"AS3": 233,
"B3": 247,
"C4": 262,
"CS4": 277,
"D4": 294,
"DS4": 311,
"E4": 330,
"F4": 349,
"FS4": 370,
"G4": 392,
"GS4": 415,
"A4": 440,
"AS4": 466,
"B4": 494,
"C5": 523,
"CS5": 554,
"D5": 587,
"DS5": 622,
"E5": 659,
"F5": 698,
"FS5": 740,
"G5": 784,
"GS5": 831,
"A5": 880,
"AS5": 932,
"B5": 988,
"C6": 1047,
"CS6": 1109,
"D6": 1175,
"DS6": 1245,
"E6": 1319,
"F6": 1397,
"FS6": 1480,
"G6": 1568,
"GS6": 1661,
"A6": 1760,
"AS6": 1865,
"B6": 1976,
"C7": 2093,
"CS7": 2217,
"D7": 2349,
"DS7": 2489,
"E7": 2637,
"F7": 2794,
"FS7": 2960,
"G7": 3136,
"GS7": 3322,
"A7": 3520,
"AS7": 3729,
"B7": 3951,
"C8": 4186,
"CS8": 4435,
"D8": 4699,
"DS8": 4978
}

# Song to be played
song = ["E5","G5","A5","P","E5","G5","B5","A5","P"]
song2 = ["D2","CS2","C2","B1"] #  D, C#, C, B
song3 = ["AS1","A1","GS1","G1","G1"] # B-flat/A#, A, A-flat/G# and G

def playtone(frequency):
    buzzer.duty_u16(1000)
    buzzer.freq(frequency)

def bequiet():
    buzzer.duty_u16(0)

def playsong(mysong):
    for i in range(len(mysong)):
        if (mysong[i] == "P"):
            bequiet()
        else:
            playtone(tones[mysong[i]])
        sleep(0.3)
    bequiet()

# If switch is on the board will alternate between 2 states: led on + song + servo at max pos or led off + song3 + servo at min pos
# If switch is off, then nothing will happen
while True:
    if switch.value() == 1:
        #speaker.on()
        led.toggle()
        servo.value = 1
        playsong(song)
        sleep(1)
        #speaker.off()
        led.toggle()
        servo.value = 0
        playsong(song3)
        sleep(1)
    else:
       sleep(1) 

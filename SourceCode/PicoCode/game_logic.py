import machine
from servo import Servo
import time
import buzzer_music

# Setup buzzer
buzzer = machine.Pin("GP17", machine.Pin.OUT)
song = "0 C#5 6 41;6 D#5 6 41;12 G#4 4 41;16 D#5 6 41;22 F5 6 41;28 G#5 1 41;29 F#5 1 41;30 F5 1 41;31 D#5 1 41;32 C#5 6 41;38 D#5 6 41;44 G#4 4 41"
mySong = buzzer_music.music(song, pins=[machine.Pin("GP17")])
my_servo = Servo(pin_id="GP15")

glb_time = 0.0
music_stop_time = 3
game_running = True
song_glb_timer = 0
servo_sweep_speed = 1
servo_alt = False
servo_angle = 0
once_after_resume = False
scan_timer = 0
scan_time = 3
delta_time = 40


# Function to handle buzzer control
def on_input(data):
    global game_running
    global song_glb_timer
    global scan_timer

    print(data)
    if data.lower() == "start":
        # Start the buzzer
        # mySong.resume()
        game_running = True
        print("Buzzer started")
    elif "mov" in data.lower():
        # Stop the buzzer
        scan_timer = glb_time + scan_time
        song_glb_timer = glb_time + scan_time
        mySong.stop()
        x_cord = float(data.split(" ")[1])
        my_servo.write(x_cord)


# Function to handle non-blocking delay
def game_loop(timer):
    if not game_running:
        return

    global glb_time
    global servo_angle
    global servo_alt
    global my_servo
    global once_after_resume
    global scan_timer
    glb_time += delta_time / 1000.0

    if song_glb_timer < glb_time and scan_timer < glb_time:
        if not once_after_resume:
            mySong.restart()
            once_after_resume = True
        mySong.tick()

    elif scan_timer > glb_time:
        mySong.stop()
        once_after_resume = False
        buzzer.value(0)

        if servo_alt:
            servo_angle -= servo_sweep_speed
        else:
            servo_angle += servo_sweep_speed

        if servo_angle >= 180 or servo_angle <= 0:
            servo_alt = not servo_alt
        my_servo.write(servo_angle)

import machine
import socket
import network
import buzzer_music
from servo import Servo
import time
import random
from machine import I2C
from vl53l1x import VL53L1X

# Configure Wi-Fi connection
wifi_ssid = "TPHotspot"
wifi_password = "lfut5895"
server_ip = "0.0.0.0"
server_port = 12345

ledred = machine.Pin("GP0", machine.Pin.OUT)  # TODO: Change to correct Pin
ledgreen = machine.Pin("GP1", machine.Pin.OUT)  # TODO: Change to correct Pin
# Initialize Wi-Fi
wifi = network.WLAN(network.STA_IF)
wifi.active(True)
wifi.connect(wifi_ssid, wifi_password)

ledred.on()
# Wait until connected
while not wifi.isconnected():
    try:
        print("Trying to connect...")
        print(wifi.scan())
        print(wifi.status())
        wifi.connect(wifi_ssid, wifi_password)
        print("not connected.")
        machine.soft_reset()
    except OSError as error:
        print(f"error is {error}")

# Print Pico's IP address
ip_address = wifi.ifconfig()[0]
print("Pico IP address:", ip_address)
ledgreen.on()

# Setup all the components

buzzer = machine.Pin("GP2", machine.Pin.OUT)
# Time, Note, Duration, Instrument (onlinesequencer.net schematic format)
# 0 D4 8 0;0 D5 8 0;0 G4 8 0;8 C5 2 0;10 B4 2 0;12 G4 2 0;14 F4 1 0;15 G4 17 0;16 D4 8 0;24 C4 8 0
main_song = "0 C#5 6 41;6 D#5 6 41;12 G#4 4 41;16 D#5 6 41;22 F5 6 41;28 G#5 1 41;29 F#5 1 41;30 F5 1 41;31 D#5 1 41;32 C#5 6 41;38 D#5 6 41;44 G#4 4 41"
start_sound = "0 E5 5 41; 10 E5 5 41; 20 E5 5 41; 30 E6 10 41"
sad_trombone = "0 A#1 6 41; 6 A1 6 41: 12 G#1 6 41; 18 G1 12 41"
pointing_servo = Servo(pin_id="GP27")
mySong = buzzer_music.music(main_song, pins=[buzzer])
i2c = I2C(id=0, sda=machine.Pin("GP4"), scl=machine.Pin("GP5"), freq=400000)
# switch = machine.Pin(
#     "GP28", machine.Pin.IN, machine.Pin.PULL_UP
# )  # TODO: Change to correct Pin
button = machine.Pin(
    "GP28", machine.Pin.IN, machine.Pin.PULL_UP
)  # TODO: Change to correct Pin

print(i2c.scan())
distance = VL53L1X(i2c)
# distance = None
# Global variables
ledred.on()


game_running = False
game_won = False
game_lost = False
music_playing = False
last_movement_time = 0
scan_start_time = 0
scanning = False
data_glb = ""
reset_servo_once = False
playing_time = random.randrange(1500, 4000)
stopping_time = random.randrange(1500, 4000)


def clamp(n, min, max):
    if n < min:
        return min
    elif n > max:
        return max
    else:
        return n


# Not used anymore
def on_input(data):
    global game_running, last_movement_time, scanning, data_glb, game_lost
    print(data)
    data_glb = data
    # Start functionality moved to main loop
    if data.lower() == "start":
        # Start the buzzer
        mySong.resume()
        game_running = True
        print("Buzzer started")
        # last_movement_time = time.ticks_ms()
    # Funtionality moved to game_loop
    # data is for example mov 180, for movement sensed in 180 degrees
    elif "mov" in data.lower() and scanning and not game_won:
        # Stop the buzzer
        # if scanning:
        print(int(data.split(" ")[1]))
        x_cord = 140 - (int(data.split(" ")[1]) * 0.3)
        print(x_cord)
        x_cord = clamp(x_cord - 5, 40, 140)
        print(x_cord)

        # scanning = False
        pointing_servo.write(x_cord)
        game_lost = True
        # game_running = False
        mySong.stop()
        buzzer.off()
        # last_movement_time = time.ticks_ms()
        # sweep_start_time += 5000
        # pause_sweeping = True


# Main game loop
def game_loop(timer):
    global game_running, last_movement_time, scanning, data_glb, distance, music_playing, scan_start_time, game_won, game_lost, mySong, reset_servo_once, playing_time, stopping_time
    # Check for distance first for the winning condition
    try:
        # print(distance.read())
        if distance is not None and game_running:
            if distance.read() < 200:

                game_won = True
                mySong.stop()
                buzzer.off()
                return
    except:
        print("Cant read distance.")
        pass

    mySong.tick()
    if not game_running or game_won or game_lost:
        buzzer.off()
        mySong.stop()
        return

    # print(data)
    # data_glb = data
    # print(distance.read())

    current_time = time.ticks_ms()
    # What is this for ?

    # should try to randomize timer, probably between 500ms and 2000ms or something like that
    # Only execute if music is playing
    # print(
    #     "Current: ",
    #     current_time,
    #     " Last mov: ",
    #     last_movement_time,
    #     " Music_playing:",
    #     music_playing,
    #     "Diff: ",
    #     time.ticks_diff(current_time, last_movement_time),
    # )
    if (
        time.ticks_diff(current_time, last_movement_time) > playing_time
        and music_playing
    ):
        mySong.stop()
        buzzer.off()
        print("Buzzer Stopped.")
        music_playing = False
        scan_start_time = time.ticks_ms()
        buzzer.off()
        ledred.value(1)
        ledgreen.value(0)
        time.sleep(1)
        scanning = True
        reset_servo_once = False
        # scanning = True
        # pause_sweeping = False

    # Only if music is not playing
    if music_playing == False:
        # should try to randomize the scanning timer, probably between 500ms and 2000ms or something like that
        if time.ticks_diff(current_time, scan_start_time) > stopping_time:

            if not reset_servo_once:
                pointing_servo.write(25)
                playing_time = random.randrange(1500, 3000)
                stopping_time = random.randrange(1000, 3000)
                reset_servo_once = True
            scanning = False
            mySong.resume()
            ledred.off()
            ledgreen.on()
            last_movement_time = current_time
            music_playing = True

            print("Buzzer resumed")


# Setup server socket
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((server_ip, server_port))
server_socket.listen(1)

print("Server is listening...")

# Accept incoming connections
conn, addr = server_socket.accept()
print("Connected to:", addr)
connected = True
ledred.off()
buzzer.off()

# Set up a timer for non-blocking delay
timer = machine.Timer()
delta_time = 40  # Time in milliseconds
timer.init(period=delta_time, mode=machine.Timer.PERIODIC, callback=game_loop)

# Main loop, runs game loop while game_running is True
song_playing = False
while True:
    # Game starts when button is pressed(button.value() = 0)
    if button.value() == 0 and connected:
        # Game starting sequence, https://wokwi.com/projects/396697502778161153 as simulation
        pointing_servo.write(25)
        ledgreen.off()
        ledred.off()
        for i in range(3):
            ledred.on()
            time.sleep(0.2)
            ledred.off()
            time.sleep(0.5)
        ledgreen.on()
        time.sleep(0.2)
        # Game starts
        game_running = True
        music_playing = True
        print("Game started")
        mySong.restart()
        ledgreen.on()
        last_movement_time = time.ticks_ms()
        while game_running:
            data_glb = conn.recv(1024).decode().strip()
            # if data_glb:
            on_input(data_glb)
            # Maybe pass the timer from here
            # random.seed(time.time_ns())
            # timer = random.randint(500, 2000)
            # timer2 = random.randint(500, 2000)
            # game_loop(None)

            if game_won:
                # Do something to signify winning, at least green led on for x duration, maybe play a different song if possible

                ledgreen.on()
                ledred.off()
                music_playing = False
                game_running = False
                scanning = False
                game_won = False
                game_lost = False

                for i in range(5):
                    ledgreen.on()
                    time.sleep(0.5)
                    ledgreen.off()
                    time.sleep(0.5)
                ledgreen.on()
                break

            if game_lost:
                print("Game Lost called")
                # mySong.song = trombone
                # mySong.restart()
                # Do something to signify losing, at least red led on for x duration, maybe play a different song if possible
                ledred.on()
                ledgreen.off()
                buzzer.off()
                # TODO: Check if buzzer_music can switch and play 2 different songs from same program, should be possible
                # mySong = buzzer_music.music(trombone, pins=[machine.Pin("GP17")])
                # mySong.restart()
                music_playing = False
                game_running = False
                scanning = False
                game_won = False
                game_lost = False

                for i in range(5):
                    ledred.on()
                    time.sleep(0.5)
                    ledred.off()
                    time.sleep(0.5)
                ledgreen.on()
                break

import machine
import socket
import network
import buzzer_music
from servo import Servo
import time

# Configure Wi-Fi connection
wifi_ssid = "A"
wifi_password = "12345678"
server_ip = "0.0.0.0"
server_port = 12345

# Initialize Wi-Fi
wifi = network.WLAN(network.STA_IF)
wifi.active(True)
wifi.connect(wifi_ssid, wifi_password)

# Wait until connected
while not wifi.isconnected():
    try:
        print("Trying to connect...")
        print(wifi.scan())
        wifi.connect(wifi_ssid, wifi_password)
        print("not connected.")
        machine.soft_reset()
    except OSError as error:
        print(f"error is {error}")

# Print Pico's IP address
ip_address = wifi.ifconfig()[0]
print("Pico IP address:", ip_address)

# Setup buzzer
buzzer = machine.Pin("GP17", machine.Pin.OUT)
song = "0 C#5 6 41;6 D#5 6 41;12 G#4 4 41;16 D#5 6 41;22 F5 6 41;28 G#5 1 41;29 F#5 1 41;30 F5 1 41;31 D#5 1 41;32 C#5 6 41;38 D#5 6 41;44 G#4 4 41"
mySong = buzzer_music.music(song, pins=[machine.Pin("GP17")])
my_servo = Servo(pin_id="GP15")


glb_time = 0.0
pause_time_on_detect = 3
game_running = False
song_glb_timer = 0
servo_sweep_speed = 1
servo_alt = False
servo_angle = 0
once_after_resume = False
scanned_once = False
scan_timer = 0
scan_time = 3
lock_timer = 0
song_playing = False


# Function to handle buzzer control
def on_input(data):
    global game_running
    global song_glb_timer
    global scan_timer
    global lock_timer
    print(data)
    if data.lower() == "start":
        # Start the buzzer
        # mySong.resume()
        game_running = True
        print("Buzzer started")
    elif "mov" in data.lower():
        # Stop the buzzer
        if song_glb_timer > glb_time:
            print("song still playing so not matter")
            return
        song_glb_timer = glb_time + pause_time_on_detect
        # scan_timer = glb_time + pause_time_on_detect
        lock_timer = glb_time + pause_time_on_detect
        print("stopped", song_glb_timer)

        mySong.stop()
        x_cord = float(data.split(" ")[1])
        my_servo.write(x_cord)


# Function to handle non-blocking delay
def game_loop(timer):
    print(" ")
    if not game_running:
        return

    global glb_time
    global servo_angle
    global servo_alt
    global my_servo
    global once_after_resume
    global scan_timer
    global scanned_once
    global song_glb_timer

    glb_time += delta_time / 1000.0

    if scan_timer < glb_time:
        if not scanned_once:
            scan_timer = glb_time + scan_time
            print("scanning for: ", scan_timer)
            scanned_once = True

    else:
        if lock_timer > glb_time:
            return
        print("scanning...")
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
        song_glb_timer = glb_time + 3

        if song_glb_timer > glb_time:
            if not once_after_resume:
                mySong.restart()
                once_after_resume = True
                scanned_once = False
            mySong.tick()
            print("playing music")


# Setup server socket
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((server_ip, server_port))
server_socket.listen(1)

print("Server is listening...")

# Accept incoming connections
conn, addr = server_socket.accept()
print("Connected to:", addr)


# Set up a timer for non-blocking delay
timer = machine.Timer()
delta_time = 40  # Time in milliseconds
timer.init(period=delta_time, mode=machine.Timer.PERIODIC, callback=game_loop)

# Main loop
song_playing = False
while True:
    data = conn.recv(1024).decode().strip()
    if data:
        on_input(data)

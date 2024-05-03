import machine
import socket
import network
import buzzer_music
from servo import Servo
import time
from machine import I2C
from vl53l1x import VL53L1X

# Configure Wi-Fi connection
wifi_ssid = "panoulu"
wifi_password = ""
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
        print(wifi.status())
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
my_servo = Servo(pin_id="GP6")
i2c = I2C(id=0, sda=machine.Pin("GP4"), scl=machine.Pin("GP5"), freq=400000)
ledred = machine.Pin("GP1", machine.Pin.OUT)  # TODO: Change to correct Pin
ledgreen = machine.Pin("GP2", machine.Pin.OUT)  # TODO: Change to correct Pin
# switch = machine.Pin(
#     "GP28", machine.Pin.IN, machine.Pin.PULL_UP
# )  # TODO: Change to correct Pin
button = machine.Pin(
    "GP26", machine.Pin.IN, machine.Pin.PULL_UP
)  # TODO: Change to correct Pin

print(i2c.scan())
distance = VL53L1X(i2c)

game_running = False
last_movement_time = 0
scanning = False
sweep_start_time = 0
pause_sweeping = True
data_glb = ""


def on_input(data):
    global game_running, last_movement_time, scanning, sweep_start_time, pause_sweeping, data_glb
    print(data)
    data_glb = data
    if data.lower() == "start":
        # Start the buzzer
        mySong.resume()
        game_running = True
        print("Buzzer started")
        last_movement_time = time.ticks_ms()
    # data is for example mov 180, for movement sensed in 180 degrees
    elif "mov" in data.lower():
        # Stop the buzzer
        if scanning:
            x_cord = float(data.split(" ")[1])
            scanning = False
            my_servo.write(x_cord)
            last_movement_time = time.ticks_ms()
            sweep_start_time += 5000
            pause_sweeping = True


# Function to handle non-blocking delay
def game_loop(timer):
    global game_running, last_movement_time, scanning, sweep_start_time, pause_sweeping, data_glb, distance, button, ledred, ledgreen
    try:
        print(distance.read())
        if distance.read() < 20:
            game_running = False
            mySong.stop()
    except:
        print("Cant read distance.")
        pass

    if not game_running:
        print(button.value())
        if button.value() == 0:
            # Game starting sequence, https://wokwi.com/projects/396697502778161153 as simulation
            for i in range(4):
                ledred.on()
                time.sleep(0.3)
                ledred.off()
                time.sleep(0.70)
            ledgreen.on()
            time.sleep(0.6)
            ledgreen.off()
            time.sleep(0.4)

        return

    print(distance.read())

    current_time = time.ticks_ms()
    mySong.tick()
    if time.ticks_diff(current_time, last_movement_time) > 10000:
        mySong.stop()
        print("Buzzer Stopped.")
        scanning = True
        pause_sweeping = False

        # Start servo sweeping for 5 seconds
        sweep_start_time = time.ticks_ms()
        while time.ticks_diff(current_time, sweep_start_time) < 10000:
            # Sweep servo
            # if scanning and not pause_sweeping:
            # angle = (
            #     (current_time % 5000) / 5000 * 180
            # )  # Sweep over 180 degrees in 5 seconds
            # my_servo.write(angle)

            current_time = time.ticks_ms()
            if time.ticks_diff(current_time, last_movement_time) < 10000:
                break
        # If no movement detected for 5 seconds after servo sweep, resume buzzer
        if time.ticks_diff(current_time, last_movement_time) > 5000:
            mySong.resume()
            last_movement_time = current_time
            print("Buzzer resumed")


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
    data_glb = conn.recv(1024).decode().strip()
    if data_glb:
        on_input(data_glb)

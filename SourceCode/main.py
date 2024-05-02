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

# Setup all the components

buzzer = machine.Pin("GP17", machine.Pin.OUT)
# Time, Note, Duration, Instrument (onlinesequencer.net schematic format)
# 0 D4 8 0;0 D5 8 0;0 G4 8 0;8 C5 2 0;10 B4 2 0;12 G4 2 0;14 F4 1 0;15 G4 17 0;16 D4 8 0;24 C4 8 0
song = "0 C#5 6 41;6 D#5 6 41;12 G#4 4 41;16 D#5 6 41;22 F5 6 41;28 G#5 1 41;29 F#5 1 41;30 F5 1 41;31 D#5 1 41;32 C#5 6 41;38 D#5 6 41;44 G#4 4 41"
start = "0 E5 5 41; 10 E5 5 41; 20 E5 5 41; 30 E6 10 41"
trombone = "0 A#1 6 41; 6 A1 6 41: 12 G#1 6 41; 18 G1 12 41"
#mySong = buzzer_music.music(song, pins=[machine.Pin("GP17")])
my_servo = Servo(pin_id="GP15")
i2c = I2C(id=0, sda=machine.Pin("GP4"), scl=machine.Pin("GP5"), freq=400000)
#ledred = machine.Pin(GP2, machine.Pin.OUT) #TODO: Change to correct Pin
#ledgreen = machine.Pin(GP14, machine.Pin.OUT)  #TODO: Change to correct Pin
#switch = machine.Pin(GP28, machine.Pin.IN, machine.Pin.PULL_UP) #TODO: Change to correct Pin
#button = machine.Pin(GP26, machine.Pin.IN, machine.Pin.PULL_UP) #TODO: Change to correct Pin

print(i2c.scan())
distance = VL53L1X(i2c)

#Global variables

game_running = False
game_won = False
game_lost = False
music_playing = False
last_movement_time = 0
scan_start_time = 0
scanning = False
sweep_start_time = 0
pause_sweeping = True
data_glb = ""

#Not used anymore
def on_input(data):
    global game_running, last_movement_time, scanning, sweep_start_time, pause_sweeping, data_glb
    print(data)
    data_glb = data
    #Start functionality moved to main loop
    if data.lower() == "start":
        # Start the buzzer
        mySong.resume()
        game_running = True
        print("Buzzer started")
        last_movement_time = time.ticks_ms()
    #Funtionality moved to game_loop
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


# Main game loop
def game_loop(data):
    global game_running, last_movement_time, scanning, sweep_start_time, pause_sweeping, data_glb, distance
    # Check for distance first for the winning condition
    try:
        print(distance.read())
        if distance.read() < 200:
            game_running = False
            game_won = True
            mySong.stop()
    except:
        print("Cant read distance.")
        pass
    if not game_running:
        return
    
    print(data)
    data_glb = data
    #print(distance.read())

    current_time = time.ticks_ms()
    mySong.tick() # What is this for ?
   
    #should try to randomize timer, probably between 500ms and 2000ms or something like that
    #Only execute if music is playing
    if time.ticks_diff(current_time, last_movement_time) and music_playing > 2000:
        mySong.stop()
        print("Buzzer Stopped.")
        music_playing = False
        scan_start_time = time.ticks_ms()
        #scanning = True
        #pause_sweeping = False
    
    #Only if music is not playing
    if music_playing == False:
        #should try to randomize the scanning timer, probably between 500ms and 2000ms or something like that
        if time.ticks_diff(current_time, scan_start_time) < 1500:
            #Check for movement and move the servo if movement detected
            #Try to get position data from data sent from the laptop
            if "mov" in data.lower():
                game_running = False
                game_lost = True
                mySong.stop()
                x_cord = float(data.split(" ")[1])
                #my_servo.write(x_cord) #Test if works
                my_servo.write(90)
                return

        if time.ticks_diff(current_time, scan_start_time) > 1500:
            mySong.resume()
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


# Set up a timer for non-blocking delay
#timer = machine.Timer()
#delta_time = 40  # Time in milliseconds
#timer.init(period=delta_time, mode=machine.Timer.PERIODIC, callback=game_loop)

# Main loop, runs game loop while game_running is True
song_playing = False
while True:
    #Game starts when button is pressed(button.value() = 0)
    if button.value() == 0:
        #Game starting sequence, https://wokwi.com/projects/396697502778161153 as simulation
        for i in range(4):
            ledred.on()
            time.sleep(0.3)
            ledred.off()
            time.sleep(0.70)
        ledgreen.on()
        time.sleep(0.6)
        ledgreen.off()
        time.sleep(0.4)
        #Game starts
        mySong = buzzer_music.music(song, pins=[machine.Pin("GP17")])
        mySong.restart()
        game_running = True
        music_playing = True
        print("Buzzer started")
        last_movement_time = time.ticks_ms()
        while(game_running):
            data_glb = conn.recv(1024).decode().strip()
            if data_glb:
                #Maybe pass the timer from here
                #random.seed(time.time_ns())
                #timer = random.randint(500, 2000)
                #timer2 = random.randint(500, 2000)
                game_loop(data_glb)
        
        if(game_won):
            #Do something to signify winning, at least green led on for x duration, maybe play a different song if possible
            start = time.ticks_ms()
            ledgreen.on()
            current = time.ticks_ms()
            time.sleep(5)
            while time.ticks_diff(current_time, start) < 5000:
                current = time.ticks_ms()
            music_playing False
            game_won False
        
        if(game_lost)
            #Do something to signify losing, at least red led on for x duration, maybe play a different song if possible
            ledred.on()
            #TODO: Check if buzzer_music can switch and play 2 different songs from same program, should be possible
            #mySong = buzzer_music.music(trombone, pins=[machine.Pin("GP17")])
            #mySong.restart()
            time.sleep(5)
            #mySong.stop()
            music_playing False
            game_lost False
    else:
        time.sleep(0.1)
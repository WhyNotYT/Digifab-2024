import socket

# Configure server IP and port
server_ip = "192.168.179.39"  # Change this to the IP address of your Pico
server_port = 12345

# Connect to the server
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((server_ip, server_port))

while True:
    command = input("Type 'start' to activate the buzzer or 'stop' to deactivate: ")
    client_socket.sendall(command.encode())
    if command.lower() == "exit":
        break

client_socket.close()

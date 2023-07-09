import socket
import time

HOST = "192.168.1.32"  # Standard loopback interface address (localhost)
PORT = 1204  # Port to listen on (non-privileged ports are > 1023)
 

# Create socket to connect to main server
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

client_socket.connect((HOST, PORT))

client_socket.sendall(b'IsUp')

while 1:
    time.sleep(1)
    t = time.time_ns()
    client_socket.sendall(4, t.to_bytes())
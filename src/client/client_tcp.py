# Laptop is client. It connects to different servers to send messages.

import socket
import time

# Create a TCP/IP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Connect the socket to the server's address and port
server_addr = '192.168.1.136'
server_address = (server_addr, 8000)
print('Connecting to {} port {}'.format(*server_address))
sock.connect(server_address)

try:
    # Send data in a loop
    while True:
        message = b'This is Anmol speaking!'
        print('Sending "{}"'.format(message.decode()))
        sock.sendall(message)
        time.sleep(1)

        data = sock.recv(1024)
        print(data.decode())

finally:
    # Clean up the connection
    print('Closing socket')
    sock.close()

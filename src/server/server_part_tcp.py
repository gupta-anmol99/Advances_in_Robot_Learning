# Pi is the server. It listens for incoming messages.

import socket

# Create a TCP/IP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Bind the socket to a specific address and port
server_address = ('192.168.1.136', 8000)
print('Starting up on {} port {}'.format(*server_address))
sock.bind(server_address)

# Listen for incoming connections
sock.listen(1)

while True:
    # Wait for a connection
    print('Waiting for a connection...')
    connection, client_address = sock.accept()
    try:
        print('Connection from', client_address)

        # Receive and send messages continuously
        while True:
            # Receive message
            data = connection.recv(1024)
            if not data:
                print('No data received from', client_address)
                break
            print('Received "{}"'.format(data.decode()))

            # Send response
            response = 'Hi Anmol, This is Pratyusha: {}'.format(data.decode())
            connection.sendall(response.encode())

    finally:
        # Clean up the connection
        connection.close()

#
#   Hello World server in Python
#   Binds REP socket to tcp://*:5555
#   Expects b"Hello" from client, replies with b"World"
#

import time
import zmq

context = zmq.Context()
socket = context.socket(zmq.REP)
socket.bind("tcp://*:5555")

while True:
    #  Wait for next request from client
    message = bytes(socket.recv())
    decoded = message.decode('utf-8')
    print(f"Received request: {decoded}")

    #  Do some 'work'
    time.sleep(1)

    # Shutdown if message is SHUTDOWN
    if message == b"SHUTDOWN":
        socket.send(b"Shutting down")
        break

    #  Send reply back to client
    socket.send(b"World")

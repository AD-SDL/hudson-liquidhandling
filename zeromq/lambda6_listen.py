"""
Lambda6 listens for data files from the Hidex (Port 5555)
    sample sheet (csv)
    hidex data (excel or csv?)

    - lambda6 should only ever receieve data from hudson01 
        (eventually need to account for different message types, messages from hudson02?)

"""

import os
import sys
import zmq
import datetime
import json
import _thread
import threading
from subprocess import Popen


# This should probably go into a core module so that we have common
# timestamps across the system
def timestamp():
    date = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%f")
    return date


context = zmq.Context()
socket = context.socket(zmq.REP)
socket.bind("tcp://*:5555")

while True:
    message = socket.recv()
    utf8_decoded_message = message.decode("utf-8")

    if message == b"SHUTDOWN":
        socket.send(b"Shutting down")
        print (timestamp() + ": received SHUTDOWN, shutting down.")
        break

    elif message == b"PING":
        response = timestamp() + ": echo"
        socket.send(response.encode())

    else:
        # immediately pass the message off to message handler and keep listening
        # this needs to change from a system call to a thread pool
        child_message_handler = Popen(
            ["python", "./lambda6_distribute_message.py", utf8_decoded_message], start_new_session=True
        ).pid

        date = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%f")
        socket.send(b"Message received and passed to lambda6_distribute_message")

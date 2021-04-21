"""
hudson01 listens for instruction files from lambda6 (Port 5556)
    sample sheet (csv)
    hidex data (excel or csv?)

    - TODO: account for/handle different types of messages
"""

import os
import sys

# from zeromq.test.hudson01_handle_message import hudson01_handle_message
import zmq
import time
import json
import _thread
import threading
from subprocess import Popen
from hudson01_handle_message import hudson01_handle_message

# from hudson01_handle_message import hudson01_handle_message
# from hudson01_handle import hudson01_handle_message


context = zmq.Context()
socket = context.socket(zmq.REP)
socket.bind("tcp://*:5556")
print("hudson01 listening on port 5556")

while True:
    message = socket.recv()
    decoded = message.decode("utf-8")

    if message == b"SHUTDOWN":
        socket.send(b"Shutting down")
        break

    else:
        # pass message to hudson01_handle_message (no need to worry about contents of message here)
        # child_message_handler = child_pid = Popen(["python", "C:\\Users\\svcaibio\\Dev\\liquidhandling\\zeromq\\test\\hudson01_handle.py", decoded],
        #     start_new_session=True
        #     ).pid
        hudson01_handle_message(decoded)
        socket.send(b"Hudson01 received instructions")

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
import time
import json
import _thread
import threading
from subprocess import Popen
from lambda6_handle_message import lambda6_handle_message

context = zmq.Context()
socket = context.socket(zmq.REP)
socket.bind(
    "tcp://*:5555"
)  

while True:
    message = socket.recv()
    decoded = message.decode("utf-8")
    # json_decoded = json.loads(decoded)

    # print("Received message\n",
    #     json.dumps(json.loads(decoded), indent=4, sort_keys=True)
    #     )
    # print("Received message: " + str(decoded))

    if message == b"SHUTDOWN":
        socket.send(b"Shutting down")
        break

    else:  # if the message was not shut down

        # pass the message off to a message handler and keep listening (don't worry about message contents here)
        child_message_handler = child_pid = Popen(
            ["python", "./lambda6_handle_message.py", decoded], start_new_session=True
        ).pid

    socket.send(b"Message received and passed to lambda6_handle_message")

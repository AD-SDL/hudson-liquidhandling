#
#   Hello World server in Python
#   Binds REP socket to tcp://*:5555
#   Expects b"Hello" from client, replies with b"World"
#
import os
import time
import json
import zmq
from subprocess import Popen
from run_qc import run_qc

context = zmq.Context()
socket = context.socket(zmq.REP)
socket.bind("tcp://*:5555")

while True:
    #  Wait for next request from client
    message = socket.recv()
    decoded = message.decode("utf-8")
    print(
        "Received message\n", json.dumps(json.loads(decoded), indent=4, sort_keys=True)
    )

    #  Send reply back to client
    socket.send(b"World")

    #  Do some 'work'
    child_pid = Popen(["python", "./run_qc.py", "myarg"], start_new_session=True).pid

    # Shutdown if message is SHUTDOWN
    if message == b"SHUTDOWN":
        socket.send(b"Shutting down")
        break

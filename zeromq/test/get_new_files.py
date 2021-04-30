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
    #print(
    #    "Received message\n", json.dumps(decoded, indent=4, sort_keys=True)
    #)
    #  Send reply back to client
    socket.send(b"World")

    #  Do some 'work'
    data = json.loads(decoded)

    for k in data:
        # write data to file
        # with open (k, 'w', encoding='utf-8') as f:
        #     json.dump(data[k], f, ensure_ascii=False, indent=4)


        if data[k]['type'][0]=='csv':
            print ("{} is a hidex file".format(k))
            myarg = k
            myarg = "/home/brettin/liquidhandling/zeromq/test/test_data/"
            myarg += "Campaign1_hidex1_04_22_21_20210422_115215.csv"
            child_pid = Popen(["python", "./run_qc.py", myarg], start_new_session=True).pid

        elif data[k]['type'][0]=='hidex':
            print ("{} is a hidex file".format(k))
            myarg = k
            myarg = "/home/brettin/liquidhandling/zeromq/test/test_data"
            child_pid = Popen(["python", "./run_qc.py", myarg], start_new_session=True).pid

        else:
            print('cannot determine type for {}'.format(k))


    # Shutdown if message is SHUTDOWN
    if message == b"SHUTDOWN":
        socket.send(b"Shutting down")
        break

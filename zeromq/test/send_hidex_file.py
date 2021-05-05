# Monitors a filenameectory and if it sees a file or files newer that some time,
# create a manifest and send a message to the message queue.

import sys
sys.path.append('../')
sys.path.append('../../')
sys.path.append('./utils/')
sys.path.append('../utils/')
sys.path.append('../../utils/')
from manifest import generateFileManifest

import argparse
import json
import zmq
import time

context = zmq.Context()
socket = context.socket(zmq.REQ)
socket.connect("tcp://localhost:5555")

# Parse args
parser = argparse.ArgumentParser()
parser.add_argument(
        "-f", "--filename",
        help="hidex file to send",
        required=True, 
        type=str )
args = vars(parser.parse_args())
print("filename = {}".format( args["filename"] ))

# Create manifest
data = {}
data = generateFileManifest(args['filename'], "instructions")
print('dumping json doc')
print(json.dumps(data, indent=4, sort_keys=True))

# send message to queue
address = str(time.time()).split(".")[0]
message = address + "***" + json.dumps(data)
socket.send_string(message)
print(f'sent message {message}')

# socket.send_json(data)
repl = socket.recv()
print(f"Got {repl}")

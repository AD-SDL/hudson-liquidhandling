#
#   Hello World client in Python
#   Connects REQ socket to tcp://localhost:5555
#   Sends "Hello" to server, expects "World" back
#

import argparse
import zmq


# Parse args
parser = argparse.ArgumentParser()
parser.add_argument("-p", "--port", help="Port to connect to", required=True, type=int)
parser.add_argument("--host", help="host to connect to", required=True, type=str)
args = vars(parser.parse_args())

context = zmq.Context()
socket = context.socket(zmq.REQ)
socket.connect("tcp://" + args["host"] + ":" + str(args["port"]))

socket.send(b"PING")
repl = socket.recv()
print(f"Got {repl}")

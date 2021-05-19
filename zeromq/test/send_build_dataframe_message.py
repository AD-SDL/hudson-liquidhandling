# Monitors a directory and if it sees a file or files newer that some time,
# create a manifest and send a message to the message queue.

import argparse
import json
from zmq_connection import connect

context, socket = connect(port=5556, pattern="REQ")

# Parse args
parser = argparse.ArgumentParser()
parser.add_argument(
    "-f", "--json_file", help="json formatted message", required=True, type=str
)
args = vars(parser.parse_args())
print("json file = {}".format(args["json_file"]))


with open(args["json_file"], "r") as f:
    data = f.read()

# If data is not empty
if len(data) > 0:
    # Send message to queue
    socket.send_string(data)
    repl = socket.recv()
    print(f"Got {repl}")

# Done

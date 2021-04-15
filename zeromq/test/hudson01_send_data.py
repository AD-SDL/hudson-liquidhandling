# Monitors a directory and if it sees a file or files newer that some time,
# create a manifest and send a message to the message queue.

from dirmon import checkDir
from manifest import generateFileManifest
import argparse
import json
import zmq
import time

context = zmq.Context()
socket = context.socket(zmq.REQ)
socket.connect("tcp://localhost:5555")
#socket.connect("tcp://lambda6.cels.anl.gov:5555") # want to send data back to lambda 6

# Parse args
parser = argparse.ArgumentParser()
parser.add_argument('-t','--time',
        help="Seconds to look back",
        required=True,
        type=int
        )
parser.add_argument('-d','--dir',
        help="Directory to look in",
        required=True,
        type=str
        )
args = vars(parser.parse_args())
print ("time = {}, dir = {}".format(args['time'], args['dir']))


# Check dir for modified files
modified_files = checkDir(args['dir'], last_mtime=args['time'])

# If modified files
if len(modified_files) > 0:

        # address = {timestamp}-{numFiles}-{R(received) or S(sent)}
        address = str(time.time()).split(".")[0] + "-" + str(len(modified_files))

        # Create manifest
        data = {}
        for f in modified_files:
                tmp = generateFileManifest(f)
                for key, value in tmp.items():
                        data[key] = value 
        print (json.dumps(data, indent=4, sort_keys=True))

        # Send message to queue
        #socket.send_string(json.dumps(data))
        socket.send_string(address + "***" + json.dumps(data))  # find a better way to separate address from json data?
        #socket.send_json(data)
        repl = socket.recv()
        print(f"Got {repl}")

# Done


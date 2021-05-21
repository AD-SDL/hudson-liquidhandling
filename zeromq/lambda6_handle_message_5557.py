""" Generic message handler 
- write message received to log
- determine if message is formatted correctly
- call train_model  module on data files 
"""

import os
import sys
import json
import inspect
from path import Path
from utils.zmq_connection import zmq_connect
from utils.manifest import generateFileManifest
from utils.train_model import train_model

def _do_work(filenames):
    # This is the only unique thing to the handler. You have to
    # implement the method that operates on a file.
    new_filenames = []
    new_filenames = train_model(filenames)

    data = []
    if len(new_filenames) > 0:
        context, socket = zmq_connect(port=5558, pattern="REQ")

        # implement message construction and send to listener
        multi_file_manifest = {}
        for f in new_filenames:
            single_file_manifest  = generateFileManifest(f, purpose="run_inferencing")
            for k in single_file_manifest:
                multi_file_manifest[k] = single_file_manifest[k]

        socket.send_string(json.dumps(multi_file_manifest))
        repl = socket.recv()
        print(f"\nGot {repl}")
    else:
        n = inspect.stack()[0][3]
        print("\nnew_filenames is empty")
        print(f"{n} failed on {filenames}")

    return new_filenames

def lambda6_handle_message(decoded_message):
    print(f'\nHandling decoded_message: {decoded_message}')
    json_decoded = json.loads(decoded_message)
    print(f"\nHandling json_decoded: {json_decoded}")
    return_val = "PASS"

    filenames = []
    for k in json_decoded:
        file_data = json_decoded[k]
        filename = file_data["path"][0]
        print(f"\nfilename {filename}")
        filenames.append(filename)

    model_filenames = _do_work(filenames)
    print(f"\nnew files {model_filenames}")
    print(f"\nDone handling message: {json_decoded}")
    return model_filenames


def main(json_string):
    """ main gets invoked because the listener does a system call to it.
        The listener passes to main the json string.
        Therefore, when testing, make the json string in the if __main__ block.
    """

    print(f"\ncalling handle message on {json_string}")
    lambda6_handle_message(json_string)


if __name__ == "__main__":
    # execute only if run as a script
    if os.path.isfile(sys.argv[1]):
        with open(sys.argv[1], 'r') as file:
            json_string = file.read()
    else:
        json_string = sys.argv[1]

    main(json_string)

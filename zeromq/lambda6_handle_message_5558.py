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
from utils.run_inferencing import run_inferencing


def _do_work(filenames):
    # This is the only unique thing to the handler. You have to
    # implement the method that operates on a file.
    
    # TODO filenames is a string here, not list. Fix this
    
    # TODO: decide basename, don't repeat in every handle message file
    try:  
        basename = os.path.splitext(os.path.basename(filenames))[0]
        if "_model" in basename:
            basename = basename.replace("_model", "")
    except Error as e:
        basename = "basename"
        print(e)
    print(len(filenames))
    print(f"5558 BASENAME: {basename}")    
    new_filenames = run_inferencing(filenames, basename)

    data = []
    if len(new_filenames) > 0:
        multi_file_manifest = {}
        context, socket = zmq_connect(port=5559, pattern="REQ")
        for f in new_filenames:
            single_file_manifest = generateFileManifest(
                f, purpose="generate_instructions"
            )
            for k in single_file_manifest:
                multi_file_manifest[k] = single_file_manifest[k]

        socket.send_string(json.dumps(multi_file_manifest))
        repl = socket.recv()
        print(f"\nGot {repl}")
    else:
        n = inspect.stack()[0][3]
        print("new_filenames is empty")
        print(f"\n{n} failed on {filenames}")

    return new_filenames


def lambda6_handle_message(decoded_message):
    json_decoded = json.loads(decoded_message)
    print(f"\nHandling message: {json_decoded}")
    print(json_decoded)

    filenames = []
    for k in json_decoded:
        file_data = json_decoded[k]
        filename = file_data["path"][0]
        print(f"\nfilename {filename}")
        filenames.append(filename)

    new_filenames = _do_work(filename)
    print(f"\nnew files {new_filenames}")
    print(f"\nDone handling message: {json_decoded}")
    return new_filenames


def main(json_string):
    """main gets invoked because the listener does a system call to it.
    The listener passes to main the json string.
    Therefore, when testing, make the json string in the if __main__ block.
    """

    lambda6_handle_message(json_string)


if __name__ == "__main__":
    # execute only if run as a script
    if os.path.isfile(sys.argv[1]):
        with open(sys.argv[1], "r") as file:
            json_string = file.read()
    else:
        json_string = sys.argv[1]

    main(json_string)

""" Lambda6 message handler 
- write message received to log
- determine if message is formatted correctly
- write contents of message to approptiate numer of files on lambda 6
- call QC module on data files 
"""

import os
import sys
import inspect
import json
from path import Path
from utils.zmq_connection import zmq_connect
from utils.build_dataframe import build_dataframe
from utils.manifest import generateFileManifest


def _do_work(filenames):

    # TODO: decide basename, don't repeat in every handle message file
    if len(filenames) == 1:
        basename = os.path.splitext(os.path.basename(filenames[0]))[0]
    else:
        basename = "basename"

    new_filenames = []
    new_filenames = build_dataframe(filenames, basename)

    if len(new_filenames) > 0:
        multi_file_manifest = {}
        context, socket = zmq_connect(port=5557, pattern="REQ")
        for f in new_filenames:
            single_file_manifest = generateFileManifest(f, purpose="train_model")
            for k in single_file_manifest:
                multi_file_manifest[k] = single_file_manifest[k]

        print(f"MULTI FILE MANIFEST: {multi_file_manifest}")

        socket.send_string(json.dumps(multi_file_manifest))
        repl = socket.recv()
        print(f"Got {repl}")
    else:
        print("new_filenames is empty")
        n = inspect.stack()[0][3]
        print(f"{n} failed on {filenames}")

    return new_filenames


def lambda6_handle_message(json_string):

    lambda6_data_path = "/lambda_stor/data/hudson/data/"

    # * extract message address and body
    json_decoded = json.loads(json_string)

    return_val = "PASS"
    print(f"Handling message: {json_decoded}")

    filenames = []
    for k in json_decoded:
        file_data = json_decoded[k]
        filename = file_data["path"][0]
        print(f"filename: {filename}")
        filenames.append(filename)

    new_filenames = _do_work(filenames)
    print(f"\nnew files {new_filenames}")
    print(f"\nDone handling message: {json_decoded}")
    return return_val


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

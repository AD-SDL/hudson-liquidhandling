""" Lambda6 message handler 
- write message received to log
- determine if message is formatted correctly
- write contents of message to approptiate numer of files on lambda 6
- call QC module on data files 
"""

import os
import sys
import json
import pandas as pd
from utils.data_utils import parse_hidex
from utils.run_qc import run_qc
from utils.zmq_connection import zmq_connect

def lambda6_handle_message(decoded_message):

    lambda6_data_path = "/lambda_stor/data/hudson/data/"

    # * extract message address and body
    address, message_body = decoded_message.split("***")
    json_decoded = json.loads(message_body)

    return_val = "PASS"
    print(f"Handling message: {str(address)}")

    # * assign path names (on lambda6 or running locally for testing?)
    if os.path.exists(lambda6_data_path):
        # format log and data directory paths
        log_dir_path = os.path.join(lambda6_data_path, "log/")
        data_dir_path = os.path.join(lambda6_data_path, str(address) + "/")

        # * record in message_log.txt
        if not os.path.exists(os.path.dirname(log_dir_path)):
            try:
                os.makedirs(os.path.dirname(log_dir_path))
            except OSError as exc:
                print("Failed to create directory-> " + str(log_dir_path))
                raise

        # write to log file if directory exists/was created
        if os.path.exists(os.path.dirname(log_dir_path)):
            with open(
                os.path.join(log_dir_path, "message_log.txt"), "a+"
            ) as message_log:
                message_log.writelines(
                    address + "-R\n"
                )  # address = {timestamp}-{numFiles}-{R(received) or S(sent)}
                for key, value in json_decoded.items():
                    message_log.writelines("\t" + str(key) + "\n")  # filenames

        # * write data to files
        # create a folder to store data (same name as in log file)
        if not os.path.exists(os.path.dirname(data_dir_path)):
            try:
                os.makedirs(os.path.dirname(data_dir_path))
            except OSError as exc:
                print("Failed to create directory -> " + str(data_dir_path))
                raise

        # write data contents to files within folder
        if os.path.exists(os.path.dirname(data_dir_path)):
            for key, value in json_decoded.items():
                file_name = key
                data = value["data"]
                with open(
                    os.path.join(data_dir_path, os.path.basename(file_name)), "w+"
                ) as data_file:
                    data_file.writelines(data)

    _run_qc(os.path.join(data_dir_path, os.path.basename(file_name)))
    print(f"Done handling message: {str(address)}")
    return return_val

def _run_qc(file_name):

    # perform the quality control on hidex file
    df = parse_hidex(file_name)
    # values = df.loc[df["Sample"] == "Blank"].to_numpy()[:, 3].astype(float)
    values = df.loc[df["Well"] == "H1"].to_numpy()[:, -1].astype(float)
    ret_val = run_qc(values)
    print(f"result: {ret_val}")

    # TODO update database with results

    # send message to build_dataframe if the data is good
    if ret_val == 'PASS':
        context, socket = zmq_connect(port=5556, pattern='REQ')
        basename = os.path.basename(file_name)
        message = {basename : {'path' : [file_name], 
            'purpose' : ['build_dataframe'], 'type' : ['JSON'] }
            }
        socket.send_string(json.dumps(message))
        repl = socket.recv()
        print(f"Got {repl}")
    else:
        print(f'qc failed on {filename}')

    return ret_val

def main(args):
    decoded_message = sys.argv[1]
    lambda6_handle_message(decoded_message)


if __name__ == "__main__":
    # execute only if run as a script
    main(sys.argv)

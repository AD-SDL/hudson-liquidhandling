# Monitors a directory and if it sees a file or files newer that some time,
# create a manifest and send a message to the message queue.

from utils.dirmon import checkDir, find_most_recent
from utils.manifest import generateFileManifest
from utils.data_utils import excel_to_csv
from utils.archive import archive
import argparse
import json
import zmq
import time
import os
import sys


def hudson01_send_data(directory, lookback_time=None, extension=""):
    """Sends most recent file in data folder to compute cell (lambda6)"""

    time.sleep(120)  # wait 2 minutes before sending the data

    return_val = "PASS"
    context = zmq.Context()
    socket = context.socket(zmq.REQ)
    socket.connect("tcp://lambda6.cels.anl.gov:5555")

    # Check for most recent excel data (hidex data)
    modified_files = [find_most_recent(directory, extension=extension)]  # now finds only most recent file  
    #modified_files = checkDir(directory, last_mtime=lookback_time)

    # If modified files
    if len(modified_files) > 0:

        address = str(time.time()).split(".")[0] + "-" + str(len(modified_files))
        print(f"Address: {address}")

        # Create manifest
        data = {}
        files_to_archive = []

        for f in modified_files:
            if os.path.basename(f) == "archive":  # ignore archive folder
                continue
            elif (
                os.path.splitext(os.path.basename(f))[1] == ".xlsx"
            ):  # if excel file, parse and covert to csv
                csv_filepath = excel_to_csv(f)
                tmp = generateFileManifest(csv_filepath, "data")
                files_to_archive.extend([f, csv_filepath])
            else:
                tmp = generateFileManifest(f, "data")
                files_to_archive.append(f)

            for key, value in tmp.items():
                data[key] = value

        print(json.dumps(data, indent=4, sort_keys=True))

        # Send message to queue
        socket.send_string(address + "***" + json.dumps(data))
        repl = socket.recv()
        print(f"Got {repl}")

        # move used files to archive after reply received
        archive(files_to_archive, directory)

    socket.close()
    return return_val
    # Done


def main(args):
    # Parse args
    print("running hudson_send_data")
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-t", "--time", help="Seconds to look back", required=False, type=int
    )
    parser.add_argument(
        "-d", "--dir", help="Directory to look in", required=True, type=str
    )
    parser.add_argument(
        "-e", "--ext", help="File extension to check for", required=False, type=str
    )
    args = vars(parser.parse_args())
    print("time = {}, dir = {}, ext = {}".format(args["time"], args["dir"], args["ext"]))

    hudson01_send_data(args["dir"], args["time"], args["ext"])


if __name__ == "__main__":
    # execute only if run as a script
    main(sys.argv)

# Monitors a directory and if it sees a file or files newer that some time,
# create a manifest and send a message to the message queue.

from utils.dirmon import checkDir
from utils.manifest import generateFileManifest
from utils.data_utils import excel_to_csv
import argparse
import json
import zmq
import time
import os
import sys

def hudson01_send_data(directory, lookback_time): 
    return_val = "PASS"

    context = zmq.Context()
    socket = context.socket(zmq.REQ)
    socket.connect("tcp://lambda6.cels.anl.gov:5555")

    # Check dir for modified files
    modified_files = checkDir(directory, last_mtime=lookback_time)

    # If modified files
    if len(modified_files) > 0:

        # address = {timestamp}-{numFiles}-{R(received) or S(sent)}
        address = str(time.time()).split(".")[0] + "-" + str(len(modified_files))
        print(f"Address: {address}")

        # Create manifest
        data = {}
        files_to_archive = []
        for f in modified_files:

            if os.path.basename(f) == "archive": # ignore archive folder
                continue
            elif os.path.splitext(os.path.basename(f))[1] == ".xlsx": # convert if excel file 
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
        #socket.send_string(address + "***" + json.dumps(data))
        #repl = socket.recv()

        # move used files to archive after reply received
        archive(files_to_archive, directory)

        #print(f"Got {repl}")

    socket.close()
    # Done


def main(args): 
    # Parse args
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-t", "--time", help="Seconds to look back", required=True, type=int
    )
    parser.add_argument("-d", "--dir", help="Directory to look in", required=True, type=str)
    args = vars(parser.parse_args())
    print("time = {}, dir = {}".format(args["time"], args["dir"]))

    hudson01_send_data(args["dir"], args["time"])  


if __name__ == "__main__":
    # execute only if run as a script
    main(sys.argv)


def archive(filenames, directory):  
    """
    filenames = list of files to archive, [filepath1, filepath2, ect. ]
    directory = path to directory which will contain archive folder
    """
    try: 
        # create archive folder of doesn't exist
        archive_path = os.path.join(directory, "archive\\")
        if not os.path.exists(os.path.dirname(archive_path)): 
            os.makedirs(archive_path)

        # move each file into archive folder 
        for i in range(len(filenames)): 
            new_filename = os.path.join(archive_path, os.path.basename(filenames[i]))

            # if file already exists in archive, force overwrite (for testing)
            if os.path.exists(new_filename): 
                os.remove(new_filename)
            
            os.rename(filenames[i], new_filename)

    except OSError as e:
        print("Error: could not archive sent files")
        print(e)





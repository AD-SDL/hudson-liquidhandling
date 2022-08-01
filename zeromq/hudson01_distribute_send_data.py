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
import datetime
from data_senders.campaign2_data_sender import send_campaign2_data
from data_senders.dna_assembly_data_sender import send_dna_assembly_data
from data_senders.serial_dilution_384_data_sender import send_sd_384_data


def hudson01_distribute_send_data(directory, lookback_time=None, extension="", plate_id="", exp_name="", data_format=""):
    """ hudson01_distribute_send_data 

    Description: Handles sending data to lambda6 depending on data_format 

    Parameters: 
        directory: directory where data file is located
        lookback_time: maximum age of data file
        extension: extension of the data file (.xlsx, .csv)
        plate_id: ID of the assay plate used to generate the data
        exp_name: unique experiment name used to generate the data
        data_format: format of the data excel file 
            (options: 'campaign2', 'dna_assembly')
    
    """

    plate_id = "" if (isinstance(plate_id, int) and plate_id == -1) else plate_id
    time.sleep(10)  # wait before sending the data

    context = zmq.Context()
    socket = context.socket(zmq.REQ)
    socket.connect("tcp://lambda6.cels.anl.gov:5555")

    # Check for most recent excel data (hidex data)
    modified_files = [
        find_most_recent(directory, extension=extension)
    ]  # now finds only most recent file
    # modified_files = checkDir(directory, last_mtime=lookback_time)

    # If modified files
    if len(modified_files) > 0:

        address = str(time.time()).split(".")[0] + "-" + str(len(modified_files))
        print(f"Address: {address}")

        # Create manifest
        data_dict = {}
        files_to_archive = []

        for f in modified_files:
            if os.path.basename(f) == "archive":  # ignore archive folder
                continue

            elif (os.path.splitext(os.path.basename(f))[1] == ".xlsx"): 

                #* Distribute based on data_format
                if data_format == "campaign2": 
                    print("handling sending campaign 2 formatted data")
                    data_dict, files_to_archive = send_campaign2_data(f, plate_id, exp_name, data_format)
                elif data_format == "dna_assembly": 
                    print("handling sending dna assembly formatted data")
                    data_dict, files_to_archive = send_dna_assembly_data(f, plate_id, exp_name, data_format)
                elif data_format == "serial_dilution":
                    print("handling sending serial dilution 384 formatted data")
                    data_dict, files_to_archive = send_sd_384_data(f, plate_id, exp_name, data_format)
            else:
                print(f"data format {data_format} cannot be handled by send data distributor ")

        if data_dict == {}: 
            print("No data found to send in message")
        else: 
            print(json.dumps(data_dict, indent=4, sort_keys=True))

            # Send message to queue
            socket.send_string(address + "***" + json.dumps(data_dict))  
            repl = socket.recv()
            print(f"Got {repl}")

            # move used files to archive after reply received
            archive(files_to_archive, directory)

    socket.close()
    # Done


def main(args):
    # Parse args
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
    parser.add_argument(
        "-id", "--plate_id", help="Plate ID associated with the data", required=False
    )
    parser.add_argument(
        "-en", "--exp_name", help="Experiment name. (same as the dir name of the folder containing the protocol instructions)", required=False
    )
    parser.add_argument(
        "-df", "--data_format", help="Data Format. (name of protocol on hidex used to create data file))", required=False, type=str
    )
    args = vars(parser.parse_args())
    # print(
    #     "time = {}, dir = {}, ext = {}".format(args["time"], args["dir"], args["ext"])
    # )

    hudson01_distribute_send_data(args["dir"], args["time"], args["ext"], args["plate_id"], args["exp_name"], args["data_format"])


if __name__ == "__main__":
    # execute only if run as a script
    main(sys.argv)
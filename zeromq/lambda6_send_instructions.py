from utils.manifest import generateFileManifest
from utils.archive import archive
import argparse
import json
import zmq
import time
import os
import sys
sys.path.append("../rdbms/")
sys.path.append("../../rdbms/") # this is the one that works
from create_plate_functions import create_empty_plate_records

def lamdba6_send_instructions(instructions_dir, info_list):

    # * connect to port on hudson01
    context = zmq.Context()
    socket = context.socket(zmq.REQ)
    socket.connect("tcp://hudson01.bio.anl.gov:5556")
    
    # format info string (num_plates,num_wells,plate_type)
    info_string = f"{info_list[0]},{info_list[1]},{info_list[2]}"
    is_test=info_list[3]  # don't pass in message to hudson01, no need

    if os.path.isdir(instructions_dir):
        instruction_files = os.listdir(instructions_dir)

        # if there are files to send
        if len(instruction_files) > 0:

            # message address = Protocol details and timestamp
            address = os.path.basename(instructions_dir)
            print(f"Address: {address}")

            # create manifest
            data = {}
            for f in instruction_files:
                f_path = os.path.join(instructions_dir, os.path.basename(f))
                tmp = generateFileManifest(f_path, "instructions")
                for key, value in tmp.items():
                    data[key] = value
                    
            # TESTING
            print("LAMBDA6_SEND_INSTRUCTIONS")
            print(f"INFO STRING: {info_string}")

            # Send message to queue
            socket.send_string(address + "***" + info_string + "***" + json.dumps(data))
            print("Message sent to port 5556 on hudson01")
           
            # Wait for reply and 
            repl = socket.recv()
            string_repl = str(repl)
            message, info = string_repl.split("***")
            
            print(f"Got {repl}")

            num_plates, num_wells, plate_type, directory_name = info.split(",")
            directory_name = directory_name[:-1]
            
            # insert call to database here
            create_empty_plate_records(int(num_plates), int(num_wells), plate_type, directory_name,is_test)

            # archive instructions once sent correctly
            archive([instructions_dir], "/lambda_stor/data/hudson/instructions/")

    socket.close()


def main(args):
    # Parse args
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-d", "--dir", help="Directory to send", required=True, type=str
    )
    parser.add_argument(
        "-i", "--info", 
        help="Assay plate details string: num_plates num_wells plate_type dir_name", 
        required = True, 
        type = str,
        nargs = "*",
    )
    args = vars(parser.parse_args())
    print("directory sent = {}".format(args["dir"]))
   
    instructions_dir = args["dir"]  # full path
    info_list = args["info"]
    lamdba6_send_instructions(instructions_dir, info_list)


if __name__ == "__main__":
    # execute only if run as a script
    main(sys.argv)

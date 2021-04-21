from manifest import generateFileManifest
import argparse
import json
import zmq
import time
import os
import sys

def lamdba6_send_instructions(instructions_dir):

    return_val = "PASS"

    #* connect to port on hudson01
    context = zmq.Context()
    socket = context.socket(zmq.REQ)
    # socket.connect("tcp://localhost:5556")
    #socket.connect("tcp://hudson01.bio.anl.gov:5556") # to send instructions to hudson01
    
    socket.connect("tcp://localhost:5556")
   
    if os.path.isdir(instructions_dir):  
        instruction_files = os.listdir(instructions_dir)

        # if there are files in the directory to send...
        if len(instruction_files) > 0: 

            # create message address (folder name, timestamp, number files sent)
            address = str(os.path.basename(instructions_dir)) + "-" + (str(time.time())).split(".")[0] + "-" + str(len(instruction_files))
            print(f"Address: {address}")

            # create manifest
            data = {} 
            for f in instruction_files: 
                f_path = os.path.join(instructions_dir, os.path.basename(f))
                tmp = generateFileManifest(f_path, "instructions")
                for key, value in tmp.items(): 
                    data[key] = value
            #print(json.dumps(data, indent=4, sort_keys=True))

            # Send message to queue 
            socket.send_string(address + "***" + json.dumps(data))
            print("Message sent to port 5556 on hudson01")
                
            repl = socket.recv()
            print(f"Got {repl}")

    socket.close()

    return return_val


def main(args):
    # Parse args
    parser = argparse.ArgumentParser()
    parser.add_argument('-d','--dir',
            help="Directory to send",
            required=True,
            type=str
            )
    args = vars(parser.parse_args())
    print("directory sent = {}".format(args['dir']))

    instructions_dir = args['dir']  # full path 
    lamdba6_send_instructions(instructions_dir)

if __name__ == "__main__":
    # execute only if run as a script
    main(sys.argv)
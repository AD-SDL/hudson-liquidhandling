''' Hudson01 message handler 
        Message recieved will be a folder containing all generated protocol files (slvp, hso, ahk, txt)

        - write filenames to message log    
        - write contents of message to approptiate numer of files on lambda 6
        - cal run_ahk.py (complete all checks -> ok to run?)

'''

import os
import sys
import json
from run_ahk import run_ahk
from test_run_ahk import test_run_ahk

def hudson01_handle_message(decoded_message):

    #* extract message address and body
    address, message_body = decoded_message.split("***")
    json_decoded = json.loads(message_body)

    return_val = "PASS"
    print(f"Handling message on hudson01 : {str(address)}")

    # for debugging --> print out message
    # for item in json_decoded.items(): 
    #     print(item)

    hudosn01_instructions_path = "C:\\labautomation\\instructions"
    test_hudson01_instructions_path = "/Users/cstone/Desktop/liquidhandling_Git_Clone/zeromq/test"

    #* assign path names (on lambda6 or running locally for testing?)
    if os.path.exists(hudosn01_instructions_path) or os.path.exists(test_hudson01_instructions_path): 
        if os.path.exists(hudosn01_instructions_path):  # if running on lambda6
            log_dir_path = os.path.join(hudosn01_instructions_path, "log\\")
            instructions_dir_path = os.path.join(hudosn01_instructions_path,str(address) + "\\")
            print("Running on hudson01")
        elif os.path.exists(test_hudson01_instructions_path):  # if testing locally
            log_dir_path = os.path.join(test_hudson01_instructions_path, "log/")
            instructions_dir_path = os.path.join(test_hudson01_instructions_path,str(address) + "/")
            print("Running on local computer for testing")

        #* record in message_log.txt
        if not os.path.exists(os.path.dirname(log_dir_path)): 
            try: 
                os.makedirs(os.path.dirname(log_dir_path))
            except OSError as exc:
                print("Failed to create directory-> " + str(log_dir_path))
                raise

        # write to log file if directory exists/was created
        if os.path.exists(os.path.dirname(log_dir_path)): 
            with open(os.path.join(log_dir_path, "message_log.txt"), 'a+') as message_log: 
                message_log.writelines(address + "-R\n")  # address = {timestamp}-{numFiles}-{R(received) or S(sent)}
                for key,value in json_decoded.items(): 
                    message_log.writelines("\t" + str(key) + "\n")  # filenames 

        #* write data to files 
        # create a folder to store data (same name as in log file)
        if not os.path.exists(os.path.dirname(instructions_dir_path)): 
            try: 
                os.makedirs(os.path.dirname(instructions_dir_path))
            except OSError as exc:
                print("Failed to create directory -> " + str(instructions_dir_path))
                raise

        # write data contents to files within folder
        if os.path.exists(os.path.dirname(instructions_dir_path)): 
            for key,value in json_decoded.items(): 
                file_name = key
                data = value["data"]
                with open(os.path.join(instructions_dir_path, os.path.basename(file_name)), 'w+') as instruction_file: 
                    instruction_file.writelines(data)
            print(f"Instructions copied to new directory: {instructions_dir_path}")
                    
        # pass the new folder name to run_ahk (checks if ok to run on robot, if so runs .ahk file)
        #if os.path.exists(hudosn01_instructions_path):
            #run_ahk(instructions_dir_path)

        if os.path.exists(hudosn01_instructions_path): # if running on hudson01
            run_ahk(instructions_dir_path)
        elif os.path.exists(test_hudson01_instructions_path): # if running locally
            # test_run_ahk(instructions_dir_path)
            run_ahk(instructions_dir_path)
        
            
    print(f"Done handling message on hudson01: {str(address)} \n")
    return return_val


def main(args):
    decoded_message = sys.argv[1]
    hudson01_handle_message(decoded_message)


if __name__ == "__main__":
    # execute only if run as a script
    main(sys.argv)
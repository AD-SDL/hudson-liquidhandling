''' Lambda6 message handler 
- write message received to log
- determine if message is formatted correctly
- write contents of message to approptiate numer of files on lambda 6
- call QC module on data files 
'''

import os
import sys
import json


def lambda6_handle_message(decoded_message):

    lambda6_data_path = "/lambda_stor/data/hudson/data/"
    test_lambda6_data_path = "/Users/cstone/Desktop/liquidhandling_Git_Clone/zeromq/test/test_lambda6_data_dir"
        
    #* extract message address and body
    address, message_body = decoded_message.split("***")
    json_decoded = json.loads(message_body)

    return_val = "PASS"
    print(f"Handling message on lambda6")

    # for debugging --> print out message
    for key,value in json_decoded.items(): 
        print(key)    # filenames
        for value_k,value_v in value.items(): 
            print("\t" + str(value_k))
            for each in value_v: 
                print("\t\t" + str(each.strip()))

    #* record in message log, print data to files in folder with a timestamp
    # if running on lambda6
    if os.path.exists(lambda6_data_path): 
        # record in message_log
        with open(os.path.join(test_lambda6_data_path, "message_log.txt"), 'a+') as message_log: 
            message_log.writelines(address + "-R\n")  # address = {timestamp}-{numFiles}-{R(received) or S(sent)}
            for key,value in json_decoded.items(): 
                message_log.writelines("\t" + str(key) + "\n")  # filenames 
        # write files to folder on lambda6
            # TODO

    # if running locally for testing ----------------------------------------------------------
    elif os.path.exists(test_lambda6_data_path): 
        print("Running on my local computer for testing")

        # write log to message_log.txt
        with open(os.path.join(test_lambda6_data_path, "message_log.txt"), 'a+') as message_log: 
            message_log.writelines(address + "-R\n")  # address = {timestamp}-{numFiles}-{R(received) or S(sent)}
            for key,value in json_decoded.items(): 
                message_log.writelines("\t" + str(key) + "\n")  # filenames 

        # write contents of file to folder (folder name = address)
            # create folder with same name as address? 
            # write all files to that folder
            # call QC on folder with name = address ---------------------------------------------

    print("Done handling message on lambda6")
    return return_val

def main(args):
    decoded_message = sys.argv[1]
    lambda6_handle_message(decoded_message)


if __name__ == "__main__":
    # execute only if run as a script
    main(sys.argv)

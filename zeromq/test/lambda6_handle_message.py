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
    test_lambda6_data_path = "/Users/cstone/Desktop/liquidhandling_Git_Clone/zeromq/test/"
        
    #* extract message address and body
    address, message_body = decoded_message.split("***")
    json_decoded = json.loads(message_body)

    return_val = "PASS"
    print(f"Handling message: {str(address)}")

    # for debugging --> print out message
    # for item in json_decoded.items(): 
    #     print(item)
    # for key,value in json_decoded.items(): 
    #     print(key)    # filenames
    #     for value_k,value_v in value.items(): 
    #         print("\t" + str(value_k))
    #         for each in value_v: 
    #             print("\t\t" + str(each.strip()))
      
    #* assign path names (on lambda6 or running locally for testing?)
    if os.path.exists(lambda6_data_path) or os.path.exists(test_lambda6_data_path): 
        if os.path.exists(lambda6_data_path):  # if running on lambda6
            log_dir_path = os.path.join(lambda6_data_path, "log/")
            data_dir_path = os.path.join(lambda6_data_path,str(address) + "/")
            print("Running on lambda6")
        elif os.path.exists(test_lambda6_data_path):  # if testing locally
            log_dir_path = os.path.join(test_lambda6_data_path, "log/")
            data_dir_path = os.path.join(test_lambda6_data_path,str(address) + "/")
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
        if not os.path.exists(os.path.dirname(data_dir_path)): 
            try: 
                os.makedirs(os.path.dirname(data_dir_path))
            except OSError as exc:
                print("Failed to create directory -> " + str(data_dir_path))
                raise

        # write data contents to files within folder
        if os.path.exists(os.path.dirname(data_dir_path)): 
            for key,value in json_decoded.items(): 
                file_name = key
                data = value["data"]
                with open(os.path.join(data_dir_path, os.path.basename(file_name)), 'w+') as data_file: 
                    data_file.writelines(data)

    print(f"Done handling message: {str(address)}")
    return return_val


def main(args):
    decoded_message = sys.argv[1]
    lambda6_handle_message(decoded_message)


if __name__ == "__main__":
    # execute only if run as a script
    main(sys.argv)

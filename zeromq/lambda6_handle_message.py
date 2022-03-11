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
import numpy as np
from utils.data_utils import parse_hidex
from utils.run_qc import run_qc
from utils.zmq_connection import zmq_connect
sys.path.append("../rdbms/")
sys.path.append("../../rdbms/") # this is the one that works
from database_functions import update_plate_data, insert_control_qc, insert_blank_adj


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
                plate_id = value["plate_id"]
                exp_name = value["experiment_name"]
                with open(
                    os.path.join(data_dir_path, os.path.basename(file_name)), "w+"
                ) as data_file:
                    data_file.writelines(data)

                # write info file inside the same folder
                with open(
                    os.path.join(data_dir_path, "info.txt"), "w+"
                ) as info_file:
                    info_file.write(f"Plate ID: {plate_id}\n")
                    info_file.write(f"Experiment Name: {exp_name}\n")  

    print(f"calling qc on {file_name}")
    _run_qc(os.path.join(data_dir_path, os.path.basename(file_name)), plate_id, exp_name)
    print(f"Done handling message: {str(address)}")
    return return_val


def _run_qc(file_name, plate_id, exp_name):

    ret_val = "PASS"

    # perform the quality control on hidex file
    df, timestamp_list, reading_date, reading_time, data_filename = parse_hidex(file_name)  

    # Add data to db 
    update_plate_data(exp_name, plate_id, timestamp_list, df, reading_date, reading_time, data_filename)
    
    #all_data_values = df.iloc[:, -1:].copy().to_numpy().astype(float)
    blank_values = df.loc[df["Well"].str.startswith('H')].copy().to_numpy()[:, -1].astype(float)
    rows = pd.DataFrame()
    data = pd.DataFrame()
    rows = rows.append(df[["Well"]], ignore_index=True)  # .to_list()   TEST THIS
    data = data.append(df.iloc[:, -1:], ignore_index=True)  # .to_list()

    data_list = data.values.tolist() 
    data_list = [float(x[0]) for x in data_list]

    rows_list = rows.values.tolist()
    rows_list = [str(x[0]) for x in rows_list]

    data_dict = {}
    for i in range(len(rows_list)): 
        data_dict[rows_list[i]] = data_list[i]

    #print(data_dict)
    
    #check z score of blanks
    # blank_z_scores = _z_score(blank_values)
    # for z in blank_z_scores:
    #     if z >= 1.5 or z <= -1.5:
    #         print("FAIL sample has z_xcore {} >= 1.5 or <= -1.5".format(z))
    #         ret_val = "FAIL"

    # check that no blank is above a certain threshold (0.052 for now?)
    for blank_OD in blank_values: 
        #if blank_OD > 0.052: 
        if blank_OD > 0.07:
            print(f"FAIL control sample {blank_OD} has Raw OD value greater than 0.052")
            ret_val = "FAIL"

    # print(f"blanks z score qc result: {ret_val}")
    print(f"done running qc on {file_name}")
    print(f"result: {ret_val}")

    # update z score qc column in db
    insert_control_qc(exp_name, plate_id, ret_val) 
    
    # if z score qc passed, then blank adjust
    if ret_val == "PASS": 
        blank_adj_values_dict = od_blank_adjusted(data_dict)
        insert_blank_adj(exp_name, plate_id, blank_adj_values_dict)
        print("INSERTED BLANK ADJ DATA INTO TABLE")

    # send message to build_dataframe if the data is good
    if ret_val == "PASS":
        context, socket = zmq_connect(port=5556, pattern="REQ")
        basename = os.path.basename(file_name)
        print("got basename {} for filename {}".format(basename, file_name))
        message = {
            basename: {
                "path": [file_name],
                "purpose": ["build_dataframe"],
                "type": ["JSON"],
            }
        }
        socket.send_string(json.dumps(message))
        repl = socket.recv()
        print(f"Got {repl}")
    else:
        print(f"qc failed on {file_name}")

    return ret_val

def _z_score(blank_values): 
    """ _z_score
        
        Description: Calculates the z-score of all values in the list

        Parameters: 
            blank_values: list of OD data for control wells

    """
    z_scores = []
    avg = np.mean(blank_values)
    std = np.std(blank_values)
    for val in blank_values:
        z_scores.append((val - avg) / std)
    print("z-scores: {}".format(z_scores))

    return z_scores


def calculate_avg(list):
    """calculate_avg

        Description: Avarage calculations of the "H" values
    """
    avg_list = []
    pointer1 = 0
    pointer2 = 6

    while pointer1 < 6:
        
        avg_list.insert(pointer1,(float(list[pointer1]) + float(list[pointer2]))/2)
        avg_list.insert(pointer2,(float(list[pointer1]) + float(list[pointer2]))/2)
        pointer1+=1
        pointer2+=1
    
    return avg_list



def od_blank_adjusted(data_frame, time_stamps):
    print("----- BLANK ADDJUSTING -----")
    """od_blank_adjusted

        Description: Recives a data_frame and calculates blank adjusted values for each data point
        Parameters: 
            data_frame: Data itself
            time_stamps: A list that contains the time points
        
        Returns: 
            - blank_adj_data_frame: A new data frame with blank adjusted values
            - adjusted_values_list: A list of blank adjusted values (this will be used to insert the values into the database)
    """
    blank_adj_data_frame = data_frame
    adjusted_values_list = []
    for time_point in time_stamps:
    
        blank_adj_list = calculate_avg(list(data_frame[time_point][84:]))
        index = 0
        
        for data_index_num in range(1,len(data_frame)+1) :
            A = float(data_frame[time_point][data_index_num])
            if index == len(blank_adj_list):
                index = 0
            adjust = round(float(data_frame[time_point][data_index_num]) - blank_adj_list[index], 3)
            if adjust < 0:
                adjust = 0
            
            blank_adj_data_frame[time_point][data_index_num] = adjust
            adjusted_values_list.append(adjust)
            index+=1
    
    return blank_adj_data_frame, adjusted_values_list

   

def main(json_string):
    lambda6_handle_message(json_string)
    


if __name__ == "__main__":
    #execute only if run as a script
    if os.path.isfile(sys.argv[1]):
        with open(sys.argv[1], "r") as file:
            json_string = file.read()
    else:
        json_string = sys.argv[1]

    main(json_string)
    
    # df, timestamp_list, reading_date, reading_time, basename = parse_hidex('/lambda_stor/data/hudson/data/1623878974-1/Campaign1_20210615_150156_RawOD.csv')
    # od_blank_adjusted(df, timestamp_list)

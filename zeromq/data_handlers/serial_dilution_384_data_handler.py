# imports
from audioop import avg
import os
import sys
import csv 
import json
import pandas as pd
import numpy as np
from utils.run_qc import run_qc
from utils.zmq_connection import zmq_connect
#import matplotlib.pyplot as plt
sys.path.append("../rdbms/")
sys.path.append("../../rdbms/") # this is the one that works
from database_functions import update_plate_data, insert_control_qc, insert_blank_adj

def handle_sd_384_data(address, json_decoded_message):

    """handle_serial_dilution_384_data

    Description: handles data processing for serial dilution (384 well plate) formatted data messages from hudson01

    Parameters: 
        address: unique message address
        message_body: utf-8 decoded message body 

    """

    # log and save the files 
    data_dir_path, file_name, plate_id, exp_name, plot_dir_path = log_and_save(address, json_decoded_message)

    file_path = os.path.join(data_dir_path, os.path.basename(file_name))

    # parse the hidex data file
    df, timestamp_list, reading_date, reading_time, data_filename = parse_hidex_sd(file_path)

    j = 0
    for i in range(4):
        # check for contaminated controls
        print(f"calling qc on {file_path}")
        qc_result = check_for_contamination(df, timestamp_list)  # TODO reformat to produce QC df

        # print qc result 
        print(f"done running qc on {file_name}")
        print(f"result: {qc_result}")

        if qc_result == "PASS": 

            # blank adjust the data
            blank_adj_df, blank_adj_list = od_blank_adjusted(df, timestamp_list)  

            # graph blank adjusted data for each timepoint
            data_basename = data_filename.split(".")[0]
            j+=1

            if j == 4:
                print(f"Done handling message: {str(address)}")

                # send message to build_dataframe if the data is good 
                context, socket = zmq_connect(port=5556, pattern="REQ")
                basename = os.path.basename(file_path)
                print("got basename {} for filename {}".format(basename, file_path))
                message = {  # TODO: might not need to pass to build df becuase df already generated in previous step
                    basename: {
                        "path": [file_path],
                        "purpose": ["build_dataframe"],
                        "type": ["JSON"],
                    }
                }
                socket.send_string(json.dumps(message))  
                repl = socket.recv()
                print(f"Got {repl}")
                j = 0
        else:
            print(f"qc failed on {file_name}")



def log_and_save(address, json_decoded_message): 
    """log_and_save

    Description: Record message in message logs and save copy of data to files on lambda6

    Parameters: 
        address: unique message address
        json_decoded_message: decoded contents of the mesage 

    Returns: 
        data_dir_path: path to directory on lambda6 where data file was saved
        file_name: name of the data file
        plate_id: ID of the plate used to generate the data
        exp_name: name of the experiment which generated the data
        plot_dir_path: path to directory created to hold generated graphs


    """

    lambda6_data_path = "/lambda_stor/data/hudson/data/"

    # # * extract message address and body
    # address, message_body = decoded_message.split("***")
    # json_decoded = json.loads(message_body)

    # return_val = "PASS"
    #print(f"Handling message: {str(address)}")

    # * assign path names (on lambda6 or running locally for testing?)
    if os.path.exists(lambda6_data_path):
        # format log and data directory paths
        log_dir_path = os.path.join(lambda6_data_path, "log/")
        data_dir_path = os.path.join(lambda6_data_path, str(address) + "/")

        # * record in message_log.txt
        if not os.path.exists(os.path.dirname(log_dir_path)):
            try:
                os.makedirs(os.path.dirname(log_dir_path))
            except OSError as e:
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
                for key, value in json_decoded_message.items():
                    message_log.writelines("\t" + str(key) + "\n")  # filenames

        # * write data to files
        # create a folder to store data (same name as in log file)
        if not os.path.exists(os.path.dirname(data_dir_path)):
            try:
                os.makedirs(os.path.dirname(data_dir_path))
            except OSError as e:
                print("Failed to create directory -> " + str(data_dir_path))
                raise

        # write data contents to files within folder
        if os.path.exists(os.path.dirname(data_dir_path)):
            for key, value in json_decoded_message.items():
                file_name = key
                data = value["data"]
                plate_id = value["plate_id"]
                exp_name = value["experiment_name"]
                data_format = value["data_format"]
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

                # create a folder to store graphs
                plot_dir_path = os.path.join(data_dir_path, "graphs/")
                try: 
                    os.makedirs(os.path.dirname(plot_dir_path))
                    print(f"created plot directory: {plot_dir_path}")
                except OSError as e: 
                    print(f"FAILED to create directory: {plot_dir_path}")
                    raise

    return data_dir_path, file_name, plate_id, exp_name, plot_dir_path


def parse_hidex_sd(file_name):

    """parses the Hidex csv file

    Description: extract the reading date, time, and data (into dataframe)

    Parameters:
        file_name: the complete path and name of the Hidex csv file

    Returns:
        df: a pandas data frame


    """

    df = pd.DataFrame()

    # extract the reading date, time, and data (into dataframe)
    DATA = False
    with open(file_name, newline="") as csvfile:
        print(f"opened {file_name}")
        csv.QUOTE_NONNUMERIC = True
        reader = csv.reader(csvfile)
        i = 0
        for row in reader:
            i += 1
            row = [x.strip() for x in row]
            if i == 3: 
                reading_date, reading_time = row[0].split(" ")
            if len(row) > 0 and row[0] == "Plate #":
                df = pd.DataFrame(columns=row)
                DATA = True
                continue
            if DATA == True:
                df.loc[len(df.index) + 1] = row

    timestamp_list = df.columns[3:].to_list()

    # extract file basename 
    basename = os.path.basename(file_name)

    return df, timestamp_list, reading_date, reading_time, basename 

def check_for_contamination(raw_df, timepoint_list,i): 
    """check_for_contaminaton

    Description: checks data from all timepoints for contaminated blanks. 
        (All wells in Row o and P are blanks)

    Parameters: 
        raw_df = dataframe of raw OD(590) absorbance readings
        timepoint_list = list of timepoints at which the data was collected 
        (both parsed directly from hidex csv data)

    Returns: 
        ret_val: TODO

        o : 336 p:360
    """ 
    ret_val = "PASS"
    print("TODO: reformat serial dilution qc check")  #TEST
    if i == 0:
        blanks_o = raw_df.iloc[336:342,3:]
        blanks_p = raw_df.iloc[360:366,3:]
        numpy_blanks_o = blanks_o.to_numpy()
        flat_numpy_blanks_o = numpy_blanks_o.ravel().tolist()
        numpy_blanks_p = blanks_p.to_numpy()
        flat_numpy_blanks_p = numpy_blanks_p.ravel().tolist()
    elif i == 1:
        blanks_o = raw_df.iloc[342:348,3:]
        blanks_p = raw_df.iloc[366:372,3:]
        numpy_blanks_o = blanks_o.to_numpy()
        flat_numpy_blanks_o = numpy_blanks_o.ravel().tolist()
        numpy_blanks_p = blanks_p.to_numpy()
        flat_numpy_blanks_p = numpy_blanks_p.ravel().tolist()
    elif i == 2:
        blanks_o = raw_df.iloc[348:354,3:]
        blanks_p = raw_df.iloc[372:378,3:]
        numpy_blanks_o = blanks_o.to_numpy()
        flat_numpy_blanks_o = numpy_blanks_o.ravel().tolist()
        numpy_blanks_p = blanks_p.to_numpy()
        flat_numpy_blanks_p = numpy_blanks_p.ravel().tolist()
    elif i == 3:
        blanks_o = raw_df.iloc[354:360,3:]
        blanks_p = raw_df.iloc[378:,3:]
        numpy_blanks_o = blanks_o.to_numpy()
        flat_numpy_blanks_o = numpy_blanks_o.ravel().tolist()
        numpy_blanks_p = blanks_p.to_numpy()
        flat_numpy_blanks_p = numpy_blanks_p.ravel().tolist()
    else:
        print("ERROR: Incorrect plate quadrant given to check_for_contamination function")

    flat_numpy_blanks = np.concatenate((flat_numpy_blanks_o,flat_numpy_blanks_p))

    for blank_raw_OD in flat_numpy_blanks: 
        if float(blank_raw_OD) > 0.07: 
            ret_val == "FAIL"
            print(f"FAIL control sample {blank_raw_OD} has Raw OD value greater than 0.07")
            # TODO: improve transparency about which sample failed at what timepoint

    return ret_val

def calculate_avg(list_o, list_p):
    """calculate_avg

    Description: Average calculations of the "O" and "P" values (blanks/control wells)

    Parameters: 
        list: TODO

    Returns: 
        avg_list: TODO
    
    """
    avg_list = []
    for i in range(len(list_o)):
        avg_list.insert(i,(float(list_o[i]) + float(list_p[i]))/2)
    return avg_list

def od_blank_adjusted(data_frame, time_stamps,i):
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
        if i == 0:
            blank_adj_list= calculate_avg(list(data_frame[time_point][336:342]), (list(data_frame[time_point][360:366])))
        elif i == 1:
            blank_adj_list = calculate_avg(list(data_frame[time_point][342:348]), list(data_frame[time_point][366:372]))       
        elif i == 2:
            blank_adj_list_o = calculate_avg(list(data_frame[time_point][348:354]), list(data_frame[time_point][372:378]))
        elif i == 3:
            blank_adj_list_o = calculate_avg(list(data_frame[time_point][354:360]), list(data_frame[time_point][378:]))
        else:
            print("ERROR: Incorrect plate quadrant given to od_blank_adjusted function")
        
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

    # TO DO: graphing

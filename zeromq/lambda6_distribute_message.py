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
from data_handlers.dna_assembly_data_handler import handle_dna_assembly_data
from data_handlers.campaign2_data_handler import handle_campaign2_data


def lambda6_distribute_message(utf8_decoded_message):  
    """lambda6_distribute_message

    Description: log message and save data to files as backup
                 parse the decoded message and pass to the correct message handler

    Parameters: 
        decoded_message: decoded json message sent from hudson01

    """

    # * extract message address and body
    address, message_body = utf8_decoded_message.split("***")
    json_decoded_message = json.loads(message_body)
    print(f"Distributing message: {str(address)}")

    for key, value in json_decoded_message.items(): # there could be more than one data file sent in the message
        file_name = key
        data = value["data"]
        plate_id = value["plate_id"]
        exp_name = value["experiment_name"]
        data_format = value["data_format"]
        purpose = value["purpose"]

        # distribute based on message purpose
        if purpose == "data":  
            if data_format == "campaign2": 
                handle_campaign2_data(address, json_decoded_message)

            if data_format == "dna_assembly": 
                handle_dna_assembly_data(address, json_decoded_message)  


def main(json_string):
    lambda6_distribute_message(json_string)
    

if __name__ == "__main__":
    #execute only if run as a script
    if os.path.isfile(sys.argv[1]):
        with open(sys.argv[1], "r") as file:
            json_string = file.read()
    else:
        json_string = sys.argv[1]

    main(json_string)
    

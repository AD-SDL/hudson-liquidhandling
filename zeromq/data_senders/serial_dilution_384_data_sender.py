import os
import sys 
sys.path.append("..")
from utils.manifest import generateFileManifest
from utils.data_utils import excel_to_csv


def send_sd_384_data(f, plate_id, exp_name, data_format):  
    """ send_serial_dilution_384_data 

    Description: Prepares serial dilution (384 well plate) formatted data files for transfer to lambda6

    Parameters: 
        f: data file path
        plate_id: ID of the plate used to generate the data
        exp_name: name associated with the experiment (unique)
        data_format: format of the excel file 
            (options = 'campaign2', 'dna_assembly','serial_dilution')
    
    Returns: 
        data_dict: formatted dictionary of data contents and metadata
        files_to_archive: list of files that should be moved to archive folder after data message is sent

    """
    # variables to return 
    data_dict = {}
    files_to_archive = []

    csv_filepath = excel_to_csv(f)
    tmp = generateFileManifest(csv_filepath, "data", plate_id, exp_name, data_format)
    files_to_archive.extend([f, csv_filepath])
    
    for key, value in tmp.items():
        data_dict[key] = value

    return data_dict, files_to_archive

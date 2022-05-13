import os
import pandas as pd
from ...zeromq.utils.manifest import generateFileManifest


def send_dna_assembly_data(f, plate_id, exp_name, data_format):
    """ send_dna_assembly_data

    Description: Prepares dna_assembly formatted data files for transfer to lambda6

    Parameters: 
        f: data file path
        plate_id: ID of the plate used to generate the data
        exp_name: name associated with the experiment (unique)
        data_format: format of the excel file 
            (options = 'campaign2', 'dna_assembly')

    Returns: 
        data_dict: formatted dictionary of data contents and metadata
        files_to_archive: list of files that should be moved to archive folder after data message is sent 
    
    """
    # variables to return 
    data = {}
    files_to_archive = []

    csv_filepath = excel_to_csv(f)
    tmp = generateFileManifest(csv_filepath, "data", plate_id, exp_name, data_format)
    files_to_archive.extend([f, csv_filepath])
    
    for key, value in tmp.items():
        data[key] = value

    return data, files_to_archive


def excel_to_csv(filename): 
    """ excel_to_csv (for dna_assembly data format)

    Description: Extracts dna_assembly formatted data from Hidex excel file into csv file

    Parameters: 
        filename: (str) file name of the excel data 

    Returns: 
        csv_filepath: (str) file path to the generated csv data 
    
    """
    print("dna_assembly version of excel to csv called")
   
    csv_filename = None

    if os.path.exists(filename):
        excel_basename = os.path.splitext(os.path.basename(filename))[0]
        csv_filename = excel_basename + ".csv"
        csv_filepath = filename.replace(os.path.basename(filename), csv_filename)

    # convert Raw OD(590) excel sheet to new csv file
    excel_OD_data = pd.read_excel(filename, sheet_name="Results by well", index_col=None)
    excel_OD_data.to_csv(csv_filepath, encoding="utf-8", index=False)

    return csv_filepath



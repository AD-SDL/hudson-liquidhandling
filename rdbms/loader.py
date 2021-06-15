import sys
import csv
import pandas as pd
# from connect import connect

# cnx = connect()

def load_source(csv_path): 
    """
    load source plate csv file into the source_plate database table
    """
    # parse csv file
    try: 
        with open(csv_path, 'r') as csv_file: 
            # skips over the header information in the first row
            contents = pd.read_csv(csv_file, skiprows=[0])
            print(contents)
    except FileNotFoundError as e: 
        print("Cannot read in contents of source csv file")
        raise

    # format for entry into source sql table 


    # enter into source plate table


    # Todo: finish sql command
    # sql = "select * from source plate"
    # cursor = cnx.cursor()
    # results = cursor.fetchall()
    # for each in results: 
    #     print(each)

#load_source("/Users/cstone/Desktop/liquidhandling_Git_Clone/rdbms/test_data/source_plate_test.csv")

import os
import csv
from connect import connect
import pandas as pd
import numpy as np
import sys
import mysql.connector
import openpyxl
from datetime import datetime

# Function to connect to the test_bugs database
def connect_Database():

    cnx = connect()
    cursor = cnx.cursor()
    # start transaction
    cursor.execute("SET autocommit = 0")
    cursor.execute("START TRANSACTION")
    return cursor, cnx

#Function to disconnect from the test_bugs database
def disconnect_Database(cursor,cnx):

    cursor.execute("COMMIT")
    cursor.execute("SET autocommit = 1")
    cursor.close()
    cnx.close()

# Function creates empty records in the "plate" and "assay_plate" tables, considering the given plate information.
def create_empty_plate_records(num_plates, num_wells, plate_type, directory_name):    

    try:
        # Connect to the test_bugs database
        cursor,cnx = connect_Database()    
        
        #Create empty records in plate table
        for create_plate in range(0, num_plates):
            add_plate = """INSERT INTO plate (type, format, expID, date_created, time_created)
                        VALUES (%s, %s, %s, %s, %s)"""

            # Using the current time to keep track of the time when the plate information is recorded in the database 
            now = datetime.now()
            current_date = now.strftime("%m/%d/%Y")
            current_time = now.strftime("%H:%M:%S.%f")
            
            plate_data = (plate_type, num_wells, directory_name, current_date, current_time)
            # Creating a new record in the plate table for the next unique plate 
            cursor.execute(add_plate, plate_data)
            

            # Recieving plate_id back to utilize the unique plate id in the assay_plate records
            plate_id = cursor.lastrowid

            # Considering the plate format, creating a given number of records in the assay_plate table 
            for records in range(0, num_wells):
                row_num = records + 1

                #Create empty assay_plate row
                create_empty_records_assay_plate(plate_id, cursor, row_num)

                 
        print(num_plates, " Record inserted succesfully into Plate table")
        print(num_plates * num_wells, " Record inserted succesfully into Assay_Plate table")

        
    except mysql.connector.Error as error:
        print("Failed to insert record into Plate and Assay_Plate table {}".format(error))
    
    finally:
        # Disconnect from the test_bugs database
        disconnect_Database(cursor,cnx)
        print("Connection to the database is closed")
        # Function returns the list of Plate IDs that are created in the database

#-----------------------------------------------

# Creates empty records in assay plate table
def create_empty_records_assay_plate(plate_id, cursor, row_num):
    
    add_assay_plate = """INSERT INTO assay_plate (plate_id, row_num)
                                VALUES (%s, %s)"""
        
    assay_data = (plate_id, row_num)
    cursor.execute(add_assay_plate, assay_data)
    
#-----------------------------------------------
def count_rows_assay_table(cursor, plate_num):

    count="SELECT COUNT(*) FROM assay_plate WHERE plate_id = 164"
    count_rows = cursor.execute(count)
    count_rows = cursor.fetchall()
    
    return count_rows[0][0]
#-----------------------------------------------

# Function to update the records for the given plate. Accepts the data file, plate id that is going to be updated and the reading time 
def update_plate_data(new_data, plate_id, time_stamps, date, time):
    #connect to the test_bugs database
    cursor,cnx = connect_Database() 
    
    # Update the records in the assay_plate table with the given data

    if len(time_stamps) > 1:
        
        count = count_rows_assay_table(cursor, plate_id)
        row_num = count
        for val in range(len(time_stamps)-1):
            for new_rows in range(count):   
                row_num += 1
                create_empty_records_assay_plate(plate_id, cursor, row_num)

        RawOD_index = 3  
        count = 1
        for time_index in time_stamps:
            for row in range(1,len(new_data) + 1):
                update_assay_plate = "UPDATE assay_plate SET well=%s, RawOD_590=%s, Elapsed_time = %s, reading_date = %s, reading_time =%s WHERE plate_id = %s AND row_num = %s"
                plate_assay_data = (new_data['Well'][row], new_data[time_index][row], time_index, date, time, plate_id, count)
                cursor.execute(update_assay_plate, plate_assay_data)
                count+=1


    # Update plate info for the given plate_id and the timestemp
    update_plate_table = "UPDATE plate SET process_status = %s WHERE plate_id = %s"
    update_values = ("completed", plate_id)
    cursor.execute(update_plate_table, update_values)
    
    #Disconnect from the test_bugs database
    disconnect_Database(cursor, cnx)

#-----------------------------------------------
# Parsing and reading the data
def parse_hidex(filename):
    """parses the Hidex csv file

    Params:
        filename: the complete path and name of the Hidex cvs file

    Returns:
        df: a pandas data frame

    Description:


    """
    df = pd.DataFrame()
    DATA = False
    # time_stamps = []
    with open(filename, newline="") as csvfile:
        print(f"opened {filename}")
        csv.QUOTE_NONNUMERIC = True
        reader = csv.reader(csvfile)
        i = 0
        for row in reader:
            i += 1
            row = [x.strip() for x in row]
            if i == 3:
                date_time = row[0]
            if len(row) > 0 and row[0] == "Plate #":
                
                # for indx in range(3, len(row)):
                #     time_stamps.append(row[indx])
                df = pd.DataFrame(columns=row)
                DATA = True
                continue
            if DATA == True:
                df.loc[len(df.index) + 1] = row
    return df, date_time



def test(filename):
    df, date_time  = parse_hidex(filename)
    time_stamps = df.columns[3:].to_list()

    # Calling the create empty plate records function. Function returns a list of recently created Plate IDs
    #create_empty_plate_records(2, 48, "hidex", "directory_name")
    
    # Calling the update plate data function
    update_plate_data(df, 164, time_stamps, "date", "time")


    #return df


if __name__ == "__main__":
    test('/lambda_stor/data/hudson/data/1620249864-1/Campaign1_20210505_144922_RawOD.csv')

#-----------------------------------------------

#TEST if this is a plate with the info below. 
#plate_info = (6, 10, "directory_name", "plate_type")

#TODO: Read plate info from the dictionary
#num_plates, num_wells, exp_id, plate_type = dic.get('num_plates'), dic.get('num_wells'), dic.get('directory_name'), dic.get('plate_type')
#plate_info = (num_plates, num_wells, exp_id, plate_type)




#-----------------------------------------------
# TO UPDATE THE RECORDS 
#-----------------------------------------------

# TODO: Write a function to parse the data file

#with open ('/lambda_stor/data/hudson/data/Campaign1_20210504_172356.csv','r') as infile:
#    reader = csv.reader(infile, delimiter = ",")
#    title = next(reader)
#    found_section = False
#    header = None
#    for row in reader:
#        if not found_section:
#            if len(row) > 0:
#                if row[0] == "Well":
#                    header = next(reader)
#                    found_section = True
#        else:
#            if len(row)>0:
#                break

# Calling the update plate data function with the data file, plate_id and timestemp list
#update_plate_data(header, plate_id, timestemp)




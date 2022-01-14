from distutils.util import execute
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
            add_plate = """INSERT INTO plate (Type, Format, Barcode, exp_ID, Date_created, Time_created)
                        VALUES (%s, %s, %s, %s, %s, %s)"""

            # Using the current time to keep track of the time when the plate information is recorded in the database 
            now = datetime.now()
            current_date = now.strftime("%m/%d/%Y")
            current_time = now.strftime("%H:%M:%S.%f")
            
            plate_data = (plate_type, num_wells, str(create_plate + 1), directory_name, current_date, current_time)
            # Creating a new record in the plate table for the next unique plate 
            cursor.execute(add_plate, plate_data)
            

            # Recieving plate_id back to utilize the unique plate id in the assay_plate records
            plate_id = cursor.lastrowid

            # Considering the plate format, creating a given number of records in the assay_plate table 
            for records in range(0, num_wells):
                row_num = records + 1

                #Create empty assay_plate row
                create_empty_records_assay_plate(plate_id, cursor, row_num)

                 
        print(num_plates, " records inserted succesfully into Plate table")
        print(num_plates * num_wells, " records inserted succesfully into Assay_Plate table")

        
    except mysql.connector.Error as error:
        print("Failed to insert record into Plate and Assay_Plate table {}".format(error))
    
    finally:
        # Disconnect from the test_bugs database
        disconnect_Database(cursor,cnx)
        print("Empty records are created and connection to the database is closed")
        # Function returns the list of Plate IDs that are created in the database

#-----------------------------------------------
# Creates empty records in the assay plate table
def create_empty_records_assay_plate(plate_id, cursor, row_num):
    
    add_assay_plate = """INSERT INTO assay_plate (Plate_ID, Row_num)
                                VALUES (%s, %s)"""
        
    assay_data = (plate_id, row_num)
    cursor.execute(add_assay_plate, assay_data)
    
#-----------------------------------------------
# Counts the number of rows in table for the given plate_id
def count_rows_assay_table(cursor, plate_num):

    count="SELECT COUNT(*) FROM assay_plate WHERE Plate_ID = %s"
    value = plate_num
    count_rows = cursor.execute(count, (value,))
    count_rows = cursor.fetchall()
    
    return count_rows[0][0]

#-----------------------------------------------
# Finds which plate_id is associated with the given file name and plate number

def plate_id_finder(cursor, file_basename_for_data, plate_number):
    find_plate = "select Plate_ID from plate WHERE Exp_ID = %s and Barcode = %s"
    plate_info = (file_basename_for_data, plate_number)
    plate_id = cursor.execute(find_plate, plate_info)
    plate_id = cursor.fetchall()
    return plate_id[0][0]

#-----------------------------------------------
# Function to update the records for the given plate. Accepts the data file, plate id that is going to be updated and the reading time 
def update_plate_data(experiment_name, plate_number, time_stamps, new_data, date, time, file_basename_for_data, Well_type):
    #connect to the test_bugs database
    cursor,cnx = connect_Database() 

    # Find the plate_id for the given data
    plate_id = plate_id_finder(cursor, file_basename_for_data, plate_number)

    # Update the records in the assay_plate table with the given data
    if len(time_stamps) > 1:
        
        # Counting how many records exist in the table and returns the last index number
        count = count_rows_assay_table(cursor, plate_id)
        # A variable to iterate from the last index number that is in the records
        row_num = count
        #-----------------------------------------------
        # TODO: Insert a if condution to check the size of records if it needs to be extended !!!!
        #-----------------------------------------------
        # Creating new empty records in the assay_table for len(time_stamps) * format of the plate 
        for val in range(len(time_stamps)-1):
            for new_rows in range(count):   
                row_num += 1
                create_empty_records_assay_plate(plate_id, cursor, row_num)

        index_num = 1
        for time_index in time_stamps:
            for row in range(1,len(new_data) + 1):
                update_assay_plate = "UPDATE assay_plate SET Well_type =  %s, Well=%s, RawOD_590=%s, Elapsed_time = %s, Experiment_name = %s, Reading_date = %s, Reading_time =%s WHERE Plate_ID = %s AND Row_num = %s"
                plate_assay_data = (Well_type, new_data['Well'][row], new_data[time_index][row], time_index, experiment_name, date, time, plate_id, index_num)
                cursor.execute(update_assay_plate, plate_assay_data)
                index_num+=1


    # Update plate info for the given plate_id and the timestemp
    update_plate_table = "UPDATE plate SET Process_status = %s WHERE Plate_ID = %s"
    update_values = ("Completed", plate_id)
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



def main(filename):
    df, date_time  = parse_hidex(filename)
    time_stamps = df.columns[3:].to_list()

    # Calling the create empty plate records function. Function returns a list of recently created Plate IDs
    
    #create_empty_plate_records(2, 48, "Hidex", "Campaign1_20210505_144922_RawOD.csv")

    # Calling the update plate data function
    update_plate_data("Campaign1_RawOD", 1, time_stamps, df, "date", "time", "Campaign1_20210505_144922_RawOD.csv", "Control")
  
    #return df


if __name__ == "__main__":
    main('/lambda_stor/data/hudson/data/1620249864-1/Campaign1_20210505_144922_RawOD.csv')


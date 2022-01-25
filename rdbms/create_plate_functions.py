from distutils.util import execute
from hashlib import new
import os
import csv
from connect import connect
import pandas as pd
import numpy as np
import sys
import mysql.connector
import openpyxl
from datetime import datetime

#TODO:  If not insert the plate info to the database first then upload the data

#-----------------------------------------------
# Function to connect to the test_bugs database
def connect_Database():

    cnx = connect()
    cursor = cnx.cursor()
    # start transaction
    cursor.execute("SET autocommit = 0")
    cursor.execute("START TRANSACTION")
    return cursor, cnx

#-----------------------------------------------
#Function to disconnect from the test_bugs database
def disconnect_Database(cursor,cnx):

    cursor.execute("COMMIT")
    cursor.execute("SET autocommit = 1")
    cursor.close()
    cnx.close()

#-----------------------------------------------
# Creates empty records in the assay plate table
def create_empty_records_assay_plate(plate_id, cursor, row_num, num_wells):

    add_assay_plate = """INSERT INTO Test_assay_plate (Plate_ID, Row_num)
                                VALUES (%s, %s)"""
        
    assay_data = (plate_id, row_num)
    cursor.execute(add_assay_plate, assay_data)

    if row_num < (num_wells):
        row_num += 1
        return create_empty_records_assay_plate(plate_id, cursor, row_num, num_wells)
    elif row_num >= (num_wells) and row_num%(num_wells) != 0:
        row_num += 1
        return create_empty_records_assay_plate(plate_id, cursor, row_num, num_wells)
    else:
        return row_num


#-----------------------------------------------
# Counts the number of rows in table for the given plate_id
def count_rows_assay_table(cursor, plate_num):

    count="SELECT COUNT(*) FROM Test_assay_plate WHERE Plate_ID = %s"
    value = plate_num
    count_rows = cursor.execute(count, (value,))
    count_rows = cursor.fetchall()
    
    return count_rows[0][0]

#-----------------------------------------------
# Finds format of the plate for the given plate_id
def find_format(cursor, plate_id):
    plate_format ="SELECT Format FROM Test_plate WHERE Plate_ID = %s"
    value = plate_id
    format = cursor.execute(plate_format, (value,))
    format = cursor.fetchall()
    return format[0][0]

#-----------------------------------------------
# Finds which plate_id is associated with the given file name and plate number
def plate_id_finder(cursor, experiment_name, plate_number):
    find_plate = "select Plate_ID from Test_plate WHERE Exp_ID = %s and Barcode = %s"
    plate_info = (experiment_name, plate_number)
    plate_id = cursor.execute(find_plate, plate_info)
    plate_id = cursor.fetchall()
   
    if len(plate_id) == 0:
        return -1
    else:
        print("Record found in the database. Plate ID:", plate_id[0][0])    
        return plate_id[0][0]
    
#-----------------------------------------------
# Match the data rows with their elapsed time
def timestamp_tracker(time_stamps, cursor, new_data, Data_information):
#Data_information = (row_num, data_index_num, file_basename_for_data, date, time, plate_id)

    for index in range(0,len(time_stamps)):
        assay_plate_insert_data(cursor, time_stamps[index], new_data, Data_information)
        Data_information[1] = 0

#-----------------------------------------------
# Enters data into database
#def assay_plate_insert_data(cursor, time_index, new_data, row_num, data_index_num, experiment_name, date, time, plate_id):
def assay_plate_insert_data(cursor, time_index, new_data, Data_information):
    """
        Data_information [List]:

            Variables:

                row_num: Row number in the database that iterates through the extended records. Highest number equals to format * len(time_stamps)
                data_index_num: Index number that iterates through the data. Highest number equals to format of the plate
                file_basename_for_data: The name of the experiment 
                date: Experiment start date 
                time: Experiment start time 
                plate_id: Plate id 
    """
    
    Data_information[1] += 1
    
    if Data_information[1] < (len(new_data)+1):
        try:
            if new_data['Well'][Data_information[1]][0] == 'H':
                Well_type = "Control"
            else:
                Well_type = "Experimental"
    
            update_assay_plate = "UPDATE Test_assay_plate SET Well_type =  %s, Well=%s, RawOD_590=%s, Elapsed_time = %s, Experiment_name = %s, Reading_date = %s, Reading_time =%s WHERE Plate_ID = %s AND Row_num = %s"
            plate_assay_data = (Well_type, new_data['Well'][Data_information[1]], new_data[time_index][Data_information[1]], time_index, Data_information[2], Data_information[3], Data_information[4], Data_information[5], Data_information[0])
            cursor.execute(update_assay_plate, plate_assay_data)
            Data_information[0]+= 1
           
        
        except mysql.connector.Error as error:
            print("Failed to insert record into Assay_plate table {}".format(error))
        
        finally:    
            return assay_plate_insert_data(cursor, time_index, new_data, Data_information)
    #else:
     #   row_num = Data_information[0]
      #  return row_num

#-----------------------------------------------
# Enters new data into the database directly 
def upload_data_directly(experiment_name, plate_number, time_stamps, new_data, date, time, file_basename_for_data):
    try:
        cursor,cnx = connect_Database()    

        add_plate = """INSERT INTO Test_plate (Type, Process_status, Barcode, exp_ID, Format, Date_created, Time_created)
                        VALUES (%s, %s, %s, %s, %s, %s, %s)"""

        # Using the current time to keep track of the time when the plate information is recorded in the database 
        now = datetime.now()
        current_date = now.strftime("%m/%d/%Y")
        current_time = now.strftime("%H:%M:%S.%f")
                    
        plate_data = ("TODO", "Completed", str(plate_number), experiment_name, len(new_data), current_date, current_time)
        cursor.execute(add_plate, plate_data)
            
        # Recieving plate_id back to utilize the unique plate id in the assay_plate records
        plate_id = cursor.lastrowid

        row_num = 1
        for index in time_stamps:
            for data_index_num in range(1,len(new_data)+1):
                if new_data['Well'][data_index_num][0] == 'H':
                    Well_type = "Control"
                else:
                    Well_type = "Experimental"

                update_assay_plate = """INSERT INTO Test_assay_plate (Plate_ID, Well_type, Row_num, Well, RawOD_590, Elapsed_time, Experiment_name, Reading_date, Reading_time)
                                                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"""                
                plate_assay_data = (plate_id, Well_type, row_num, new_data['Well'][data_index_num], new_data[index][data_index_num], index, file_basename_for_data, date, time)
                cursor.execute(update_assay_plate, plate_assay_data)
                row_num+=1

    except mysql.connector.Error as error:
        print("Failed to insert record into Assay_plate table {}".format(error))

    finally:
        # Disconnect from the test_bugs database
        disconnect_Database(cursor, cnx)
        print("Connection to the database is closed")
    

#-----------------------------------------------
# Function creates empty records in the "plate" and "assay_plate" tables, considering the given plate information.
def create_empty_plate_records(num_plates, num_wells, plate_type, directory_name):    

    try:
        # Connect to the test_bugs database
        cursor,cnx = connect_Database()    
        
        #Create empty records in plate table
        for create_plate in range(0, num_plates):
            add_plate = """INSERT INTO Test_plate (Type, Format, Barcode, exp_ID, Date_created, Time_created)
                        VALUES (%s, %s, %s, %s, %s, %s)"""

            # Using the current time to keep track of the time when the plate information is recorded in the database 
            now = datetime.now()
            current_date = now.strftime("%m/%d/%Y")
            current_time = now.strftime("%H:%M:%S.%f")
            
            plate_data = (plate_type, num_wells, str(create_plate), directory_name, current_date, current_time)
            cursor.execute(add_plate, plate_data)

            # Recieving plate_id back to utilize the unique plate id in the assay_plate records
            plate_id = cursor.lastrowid

    
            # Considering the plate format, creating a given number of records in the assay_plate table
            row_num = 1
            create_empty_records_assay_plate(plate_id, cursor, row_num, num_wells)

        
    except mysql.connector.Error as error:
        print("Failed to insert record into Plate and Assay_Plate table {}".format(error))
    
    finally:
        # Disconnect from the test_bugs database
        print(num_plates, " records inserted succesfully into Plate table")
        print(num_plates * num_wells, " records inserted succesfully into Assay_Plate table")
        disconnect_Database(cursor, cnx)
        print("Connection to the database is closed")

#-----------------------------------------------
# Function to update the records for the given plate. Accepts the data file, plate id that is going to be updated and the reading time 
def update_plate_data(experiment_name, plate_number, time_stamps, new_data, date, time, file_basename_for_data):

    try:
        #connect to the test_bugs database
        cursor,cnx = connect_Database() 
       
        # Find the plate_id for the given data
        experiment_name = experiment_name.strip()
        plate_id = plate_id_finder(cursor, experiment_name, plate_number)
        
        if plate_id == -1:
            print("Plate record does not exists in the database!!!")
            print("Creating new records for", experiment_name, " Barcode: 0")
            upload_data_directly(experiment_name, plate_number, time_stamps, new_data, date, time, file_basename_for_data)
        else:
            # Find format of the plate
            format = find_format(cursor, plate_id)
            
            # Counting how many records exist in the table and returns the last index number
            row_num = count_rows_assay_table(cursor, plate_id) 

            # Checking if the database needs to be extended
            if len(time_stamps) * format > row_num:
                # Creating new empty record in the assay_table until len(time_stamps) * format = row_num
                for lenght_time_stamps in range(len(time_stamps)-1):
                    row_num = create_empty_records_assay_plate(plate_id, cursor, row_num +1, format)
                
            # Update the records in the assay_plate table with the given data
            row_num, data_index_num = 1, 0
            Data_information = [row_num, data_index_num, file_basename_for_data, date, time, plate_id]
            timestamp_tracker(time_stamps, cursor, new_data, Data_information)

            # Update plate info for the given plate_id and the timestemp
            update_plate_table = "UPDATE Test_plate SET Process_status = %s WHERE Plate_ID = %s"
            update_values = ("Completed", plate_id)
            cursor.execute(update_plate_table, update_values)
            
            
    except mysql.connector.Error as error:
        print("Failed to insert record into Plate and Assay_Plate table {}".format(error))
    
    finally:
        # Disconnect from the test_bugs database
        disconnect_Database(cursor, cnx)
        print(len(time_stamps)*len(new_data), "Records are inserted. Barcode:", plate_number)
        print("Connection to the database is closed")


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
                
                df = pd.DataFrame(columns=row)
                DATA = True
                continue
            if DATA == True:
                df.loc[len(df.index) + 1] = row
    return df, date_time

def add_time(date, time, time_stamp):
    date = date.split("-", 3)
    time = time.split(":",3)
    date_and_time = datetime.datetime(int(date[0]), int(date[1]), int(date[2]), int(time[0]), int(time[1]), int(time[2]))
    print(date_and_time)
    pass

    
def main(filename):
    df, date_time  = parse_hidex(filename)
    time_stamps = df.columns[3:].to_list()
    date_time = date_time.split(" ", 1)

    
    # Calling the create empty plate records function. Function returns a list of recently created Plate IDs
    #create_empty_plate_records(1, 48, "Hidex", "Campaign1_20210505_191201_RawOD.csv")
    
    # Calling the update plate data function
    update_plate_data("Campaign1_20210505_191201_RawOD.csv", 3, time_stamps, df, date_time[0], date_time[1], "Campaign1_20210505")
    

if __name__ == "__main__":
    main('/lambda_stor/data/hudson/data/1628731768/Campaign1_20210505_191201_RawOD.csv')


from distutils.util import execute
from hashlib import new
import os
import csv
from selectors import EpollSelector
from pandas.core.frame import DataFrame
from connect import connect
import pandas as pd
import numpy as np
import sys
import mysql.connector
import openpyxl
from datetime import datetime


#-----------------------------------------------
def connect_Database():
    """connect_Database

        Description: Function to connect to the test_bugs database

        Parameters: 
                
    """

    cnx = connect()
    cursor = cnx.cursor()
    # start transaction
    cursor.execute("SET autocommit = 0")
    cursor.execute("START TRANSACTION")
    return cursor, cnx

#-----------------------------------------------
def disconnect_Database(cursor,cnx):
    """disconnect_Database

        Description: Function to disconnect from the test_bugs database

        Parameters: 
                
    """

    cursor.execute("COMMIT")
    cursor.execute("SET autocommit = 1")
    cursor.close()
    cnx.close()

#-----------------------------------------------
def create_empty_records_assay_plate(Inc_ID, cursor, row_num, num_wells, Is_Test):
    """create_empty_records_assay_plate

        Description: Creates empty records in the assay plate table

        Parameters: 
            Inc_ID
            cursor
            row_num
            num_wells
            Is_Test
        Returns:
            - Recursive function, untill desired number of rows are created
            - Last row number 
    """

    if Is_Test == "true":
        table_name = "Test_assay_plate"
    elif Is_Test == "false":
        table_name = "assay_plate"


    add_assay_plate = "INSERT INTO " + table_name + "(Inc_ID, Row_num) VALUES (%s, %s)"
        
    assay_data = (Inc_ID, row_num)
    cursor.execute(add_assay_plate, assay_data)

    if row_num < (num_wells):
        row_num += 1
        return create_empty_records_assay_plate(Inc_ID, cursor, row_num, num_wells, Is_Test)
    elif row_num >= (num_wells) and row_num%(num_wells) != 0:
        row_num += 1
        return create_empty_records_assay_plate(Inc_ID, cursor, row_num, num_wells, Is_Test)
    else:
        return row_num


#-----------------------------------------------
def count_rows_assay_table(cursor, plate_num , Is_Test):
    """count_rows_assay_table

        Description: Counts the number of rows in table for the given Inc_ID

        Parameters: 
            cursor
            plate_num
            Is_Test

        Returns: Number of records in the databse of the given Plate
                        
    """
    if Is_Test == "true":
        table_name = "Test_assay_plate"
    elif Is_Test == "false":
        table_name = "assay_plate"

    count="SELECT COUNT(*) FROM " + table_name + " WHERE Inc_ID = %s"
    value = plate_num
    count_rows = cursor.execute(count, (value,))
    count_rows = cursor.fetchall()
    
    return count_rows[0][0]

#-----------------------------------------------
def find_format(cursor, Inc_ID, Is_Test):
    """find_format

        Description: Finds format of the plate for the given Inc_ID

        Parameters: 
            cursor
            Inc_ID
            Is_Test: 
        
        Returns:
            Format of the plate
            
    """

    if Is_Test == "true":
        table_name = "Test_plate"
    elif Is_Test == "false":
        table_name = "plate"

    plate_format ="SELECT Format FROM " + table_name + " WHERE Inc_ID = %s"
    value = Inc_ID
    format = cursor.execute(plate_format, (value,))
    format = cursor.fetchall()
    return format[0][0]

#-----------------------------------------------
def Inc_ID_finder(cursor, experiment_name, plate_number, Is_Test):
    """Inc_ID_finder

        Description: Finds which Inc_ID is associated with the given file name and plate number

        Parameters: 
            cursor:
            experiment_name:
            plate_number:
            Is_Test: True; records will be inserted into Test_plate & Test_assay_plate. False; records will be inserted into plate & assay_plate.
        Returns:
            -1: If Plate is not found in the database
            Inc_ID number: If plate exist in the database 
    """

    if Is_Test == "true":
        table_name = "Test_plate"
    elif Is_Test == "false":
        table_name = "plate"

    find_plate = "select Inc_ID from " + table_name + " WHERE Exp_ID = %s and Barcode = %s"
    plate_info = (experiment_name, plate_number)
    Inc_ID = cursor.execute(find_plate, plate_info)
    Inc_ID = cursor.fetchall()
    if len(Inc_ID) == 0:
        return -1
    else:
        print("Record found in the database. Inc_ID:", Inc_ID[0][0])    
        return Inc_ID[0][0]
    
#-----------------------------------------------
def timestamp_tracker(time_stamps, cursor, new_data, Data_information, Is_Test):
    """timestamp_tracker

        Description: A function to traverse the timestamp list so that elapsed times could be matched with Raw OD data

        Parameters: 
                
    """


    for index in range(0,len(time_stamps)):
        assay_plate_insert_data(cursor, time_stamps[index], new_data, Data_information, Is_Test)
        Data_information[1] = 0

#-----------------------------------------------
def assay_plate_insert_data(cursor, time_index, new_data, Data_information, Is_Test):
    """assay_plate_insert_data

        Description: Inserts the data into the assay_plate table

        Varaibles: 
            cursor:
            time_index: next time index in the time_stamps list
            new_data: Data itself in pandas Data Frame
            Data_information [List]:
                    row_num: Row number in the database that iterates through the extended records. Highest number equals to format * len(time_stamps)
                    data_index_num: Index number that iterates through the data. Highest number equals to format of the plate
                    file_basename_for_data: The name of the experiment file
                    date: Experiment start date 
                    time: Experiment start time 
                    Inc_ID: Inc_ID 
            Is_Test: True; records will be inserted into Test_plate & Test_assay_plate. False; records will be inserted into plate & assay_plate.
        Returns:
            Recursive function
    """
    Data_information[1] += 1
    
    if Data_information[1] < (len(new_data)+1):
        try:
            if new_data['Well'][Data_information[1]][0] == 'H':
                Data_group = "Control"
            else:
                Data_group = "Experimental"
            
            if Is_Test == "true":
                table_name = "Test_assay_plate"
            elif Is_Test == "false":
                table_name = "assay_plate"

            update_assay_plate = "UPDATE " + table_name + " SET Data_group =  %s, Well=%s, Raw_Value=%s, Elapsed_time = %s, Data_File_Name = %s, Reading_date = %s, Reading_time = %s, Assay_Details = %s WHERE Inc_ID = %s AND Row_num = %s"
            plate_assay_data = (Data_group, new_data['Well'][Data_information[1]], new_data[time_index][Data_information[1]], time_index, Data_information[2], Data_information[3], Data_information[4], "Row_OD(590)", Data_information[5], Data_information[0])
            cursor.execute(update_assay_plate, plate_assay_data)
            Data_information[0]+= 1
                 
        except mysql.connector.Error as error:
            print(f"Failed to insert record into {table_name}" + " table {}".format(error))
        
        finally:    
            return assay_plate_insert_data(cursor, time_index, new_data, Data_information, Is_Test)
  
#-----------------------------------------------
def upload_data_directly(experiment_name, plate_number, time_stamps, new_data, date, time, file_basename_for_data, Is_Test):
    """upload_data_directly

        Description: Enters new data into the database directly 

        Parameters: 
            experiment_name
            plate_number: Barcode number 
            time_stamps: List of start times
            new_data: Data itself in pandas Data Frame
            date: Experiment start date 
            time: Experiment start time 
            file_basename_for_data: The name of the experiment file
            Is_Test: True; records will be inserted into Test_plate & Test_assay_plate. False; records will be inserted into plate & assay_plate.     
    """
    try:
        cursor,cnx = connect_Database()    

        if Is_Test == "true":
            table_name = "Test_plate"
        elif Is_Test == "false":
            table_name = "plate"

        add_plate = "INSERT INTO " + table_name + " (Type, Process_status, Barcode, Exp_ID, Format, Date_created, Time_created) VALUES (%s, %s, %s, %s, %s, %s, %s)"

        # Using the current time to keep track of the time when the plate information is recorded in the database 
        now = datetime.now()
        current_date = now.strftime("%Y-%m-%d")
        current_time = now.strftime("%H:%M:%S.%f")
                    
        plate_data = ("Hidex", "Completed", str(plate_number), experiment_name, 96, current_date, current_time)
        cursor.execute(add_plate, plate_data)
            
        # Recieving Inc_ID back to utilize the unique plate id in the assay_plate records
        Inc_ID = cursor.lastrowid
        
        if table_name == "Test_plate":
                table_name = "Test_assay_plate"
        elif table_name == "plate":
                table_name = "assay_plate"

        row_num = 1
        for index in time_stamps:
            for data_index_num in range(1,len(new_data)+1):

                if new_data['Well'][data_index_num][0] == 'H':
                    Data_group = "Control"
                else:
                    Data_group = "Experimental"
                
                update_assay_plate = "INSERT INTO " + table_name + " (Inc_ID, Data_group, Row_num, Well, Raw_Value, Elapsed_time, Data_File_Name, Reading_date, Reading_time) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"                
                plate_assay_data = (Inc_ID, Data_group, row_num, new_data['Well'][data_index_num], new_data[index][data_index_num], index, file_basename_for_data, date, time)
                cursor.execute(update_assay_plate, plate_assay_data)
                row_num+=1

    except mysql.connector.Error as error:
        print(f"Failed to insert record into {table_name}" + " table {}".format(error))

    finally:
        # Disconnect from the test_bugs database
        disconnect_Database(cursor, cnx)
        print("Connection to the database is closed")
    

#-----------------------------------------------
def create_empty_plate_records(num_plates: int, num_wells: int, plate_type: str, directory_name: str, Is_Test: str):    
    """create_empty_plate_records

        Description: Creates empty records in the "plate" and "assay_plate" tables, considering the given plate information.

        Parameters: 
            num_plates: Number of plates
            num_wells: Number of wells
            plate_type: Type of the plate
            directory_name: Name of the experiment file
            Is_Test: True; records will be inserted into Test_plate & Test_assay_plate. False; records will be inserted into plate & assay_plate.
                
    """   
    try:
      
        # Connect to the test_bugs database
        cursor,cnx = connect_Database()    
        
        Is_Test = Is_Test.lower()
        if Is_Test != "true" and Is_Test != "false":
            raise Exception 
        
        if Is_Test == "true":
            table_name = "Test_plate"
        elif Is_Test == "false":
            table_name = "plate"

        #Create empty records in plate table
        for create_plate in range(0, num_plates):
            
            add_plate = "INSERT INTO " + table_name + " (Type, Format, Barcode, Exp_ID, Date_created, Time_created) VALUES (%s, %s, %s, %s, %s, %s)"

            # Using the current time to keep track of the time when the plate information is recorded in the database 
            now = datetime.now()
            current_date = now.strftime("%Y-%m-%d")
            current_time = now.strftime("%H:%M:%S.%f")
            
            plate_data = (plate_type, num_wells, str(create_plate), directory_name, current_date, current_time)
            cursor.execute(add_plate, plate_data)

            # Recieving Inc_ID back to utilize the unique plate id in the assay_plate records
            Inc_ID = cursor.lastrowid

    
            # Considering the plate format, creating a given number of records in the assay_plate table
            row_num = 1
            create_empty_records_assay_plate(Inc_ID, cursor, row_num, num_wells, Is_Test)



    except mysql.connector.Error as error:
        print(f"Failed to insert record into {table_name}" + " table {}".format(error))

    except Exception as err:
        print("Please enter True or False to Is_Test!!!")    

    else:
        print(num_plates, f" records inserted succesfully into {table_name} table")
        print(num_plates * num_wells, " records inserted succesfully into Assay_Plate table")
        
    finally:
        # Disconnect from the test_bugs database
        disconnect_Database(cursor, cnx)
        print("Connection to the database is closed")

#-----------------------------------------------
def update_plate_data(experiment_name: str, plate_number: int, time_stamps: list, new_data: DataFrame, date: str, time: str, file_basename_for_data: str, Is_Test: str):
    """update_plate_data

        Description: Update the records for the given plate

        Parameters: 
            experiment_name: Name of the experiment, that matches the Exp_ID in Plate table
            plate_number: Barcode number
            time_stamps: List of start times
            new_data: Data itself in pandas Data Frame
            date: Experiment start date 
            time: Experiment start time 
            file_basename_for_data: The name of the experiment file
            Is_Test: True; records will be inserted into Test_plate & Test_assay_plate. False; records will be inserted into plate & assay_plate.
            
    """
    try:
        cursor,cnx = connect_Database() 

        Is_Test = Is_Test.lower()
        if Is_Test != "true" and Is_Test != "false":
            raise Exception 
            
        #connect to the test_bugs database
       
        # Find the Inc_ID for the given data
        experiment_name = experiment_name.strip()
        Inc_ID = Inc_ID_finder(cursor, experiment_name, plate_number, Is_Test)
        
        if Inc_ID == -1:
            print("Plate record does not exists in the database!!!")
            print("Creating new records for", experiment_name, " Barcode: 0")
            upload_data_directly(experiment_name, plate_number, time_stamps, new_data, date, time, file_basename_for_data, Is_Test)
        else:
            # Find format of the plate
            format = find_format(cursor, Inc_ID, Is_Test)
            
            # Counting how many records exist in the table and returns the last index number
            row_num = count_rows_assay_table(cursor, Inc_ID, Is_Test) 

            # Checking if the database needs to be extended
            if len(time_stamps) * format > row_num:
                # Creating new empty record in the assay_table until len(time_stamps) * format = row_num
                for lenght_time_stamps in range(len(time_stamps)-1):
                    row_num = create_empty_records_assay_plate(Inc_ID, cursor, row_num +1, format, Is_Test)
                
            # Update the records in the assay_plate table with the given data
            row_num, data_index_num = 1, 0
            Data_information = [row_num, data_index_num, file_basename_for_data, date, time, Inc_ID]
            timestamp_tracker(time_stamps, cursor, new_data, Data_information, Is_Test)

            # Update plate info for the given Inc_ID and the timestemp
            if Is_Test == "true":
                table_name = "Test_plate"
            elif Is_Test == "false":
                table_name = "plate"
            update_plate_table = "UPDATE " + table_name + " SET Process_status = %s WHERE Inc_ID = %s"
            update_values = ("Completed", Inc_ID)
            cursor.execute(update_plate_table, update_values)
            
            
    except mysql.connector.Error as error:
        print("Failed to insert record into Plate and Assay_Plate table {}".format(error))
    
    except Exception as err:
        print("Please enter True or False to Is_Test")    

    else:
        print(len(time_stamps)*len(new_data), "Records are inserted. Barcode:", plate_number)
    
    finally:
        # Disconnect from the test_bugs database
        disconnect_Database(cursor, cnx)        
        print("Connection to the database is closed")


#-----------------------------------------------
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

# Currently not in use
def add_time(date, time, time_stamp):
    date = date.split("-", 3)
    time = time.split(":",3)
    date_and_time = datetime.datetime(int(date[0]), int(date[1]), int(date[2]), int(time[0]), int(time[1]), int(time[2]))
    print(date_and_time)
    pass

    
def Database_functions(filename):
    df, date_time  = parse_hidex(filename)
    time_stamps = df.columns[3:].to_list()
    date_time = date_time.split(" ", 1)

    
    Is_Test = "True"
    
    # Calling the create empty plate records function.
    #create_empty_plate_records(1, 48, "Hidex", "Campaign1_20210505_191201_RawOD.csv", Is_Test)
    
    # Calling the update plate data function
    update_plate_data("Campaign1_20210505_191201_RawOD.csv", 0, time_stamps, df, date_time[0], date_time[1], "Campaign1_20210505", Is_Test)



if __name__ == "__main__":
    Database_functions('/lambda_stor/data/hudson/data/1628731768/Campaign1_20210505_191201_RawOD.csv')


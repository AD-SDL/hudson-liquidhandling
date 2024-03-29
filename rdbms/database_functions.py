from distutils.util import execute
from hashlib import new
import os
import csv
from selectors import EpollSelector
from more_itertools import first
from pandas.core.frame import DataFrame
from connect import *
import pandas as pd
import numpy as np
import sys
import mysql.connector
import openpyxl
from datetime import *



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
    cursor = cnx.cursor(buffered=True)
    return cursor, cnx

#-----------------------------------------------
def disconnect_Database(cursor,cnx):
    """disconnect_Database

        Description: Function to disconnect from the test_bugs database

        Parameters: 
                
    """

    cursor.execute("COMMIT")
    cursor.execute("SET autocommit = 1")
    #cursor.close()
    close(cnx)

#-----------------------------------------------
def create_empty_records_assay_plate(plate_id, cursor, row_num, num_wells, Is_Test):
    """create_empty_records_assay_plate

        Description: Creates empty records in the assay plate table

        Parameters: 
            plate_id
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


    add_assay_plate = "INSERT INTO " + table_name + "(plate_id, Row_num) VALUES (%s, %s)"
        
    assay_data = (plate_id, row_num)
    cursor.execute(add_assay_plate, assay_data)

    if row_num < (num_wells):
        row_num += 1
        return create_empty_records_assay_plate(plate_id, cursor, row_num, num_wells, Is_Test)
    elif row_num >= (num_wells) and row_num%(num_wells) != 0:
        row_num += 1
        return create_empty_records_assay_plate(plate_id, cursor, row_num, num_wells, Is_Test)
    else:
        return row_num


#-----------------------------------------------
def count_rows_assay_table(cursor, plate_num , Is_Test):
    """count_rows_assay_table

        Description: Counts the number of rows in table for the given plate_id

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

    count="SELECT COUNT(*) FROM " + table_name + " WHERE plate_id = %s"
    value = plate_num
    count_rows = cursor.execute(count, (value,))
    count_rows = cursor.fetchall()
    
    return count_rows[0][0]

#-----------------------------------------------
def find_format(cursor, plate_id, Is_Test):
    """find_format

        Description: Finds format of the plate for the given plate_id

        Parameters: 
            cursor
            plate_id
            Is_Test: 
        
        Returns:
            Format of the plate
            
    """

    if Is_Test == "true":
        table_name = "Test_plate"
    elif Is_Test == "false":
        table_name = "plate"

    plate_format ="SELECT Format FROM " + table_name + " WHERE plate_id = %s"
    value = plate_id
    format = cursor.execute(plate_format, (value,))
    format = cursor.fetchall()
    return format[0][0]

#-----------------------------------------------
def plate_id_finder(cursor, experiment_name, plate_number):
    """plate_id_finder

        Description: Finds which plate_id is associated with the given file name and plate number

        Parameters: 
            cursor:
            experiment_name:
            plate_number:
        Returns:
            -1: If Plate is not found in the database
            plate_id number and table_name: If plate exist in the database 
    """

    find_plate = "select plate_id from Test_plate WHERE Exp_ID = %s and Barcode = %s"
    plate_info = (experiment_name, plate_number)
    plate_id = cursor.execute(find_plate, plate_info)
    plate_id = cursor.fetchall()
    
    if len(plate_id) != 0:
        print("Record found in the database. plate_id:", plate_id[0][0])   
        return plate_id[0][0], "Test_plate"

    find_plate = "select plate_id from plate WHERE Exp_ID = %s and Barcode = %s"
    plate_info = (experiment_name, plate_number)
    plate_id = cursor.execute(find_plate, plate_info)
    plate_id = cursor.fetchall()
    
    if len(plate_id) != 0:
        print("Record found in the database. plate_id:", plate_id[0][0])   
        return plate_id[0][0], "plate"
    else:
        return -1, "NULL"
    
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
                    plate_id: plate_id 
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

            update_assay_plate = "UPDATE " + table_name + " SET Data_group =  %s, Well=%s, Raw_Value=%s, Elapsed_time = %s, Data_File_Name = %s, Reading_date = %s, Reading_time = %s, Assay_Details = %s WHERE plate_id = %s AND Row_num = %s"
            plate_assay_data = (Data_group, new_data['Well'][Data_information[1]], new_data[time_index][Data_information[1]], time_index, Data_information[2], Data_information[3], Data_information[4], "Row_OD(590)", Data_information[5], Data_information[0])
            cursor.execute(update_assay_plate, plate_assay_data)
            Data_information[0]+= 1
                 
        except mysql.connector.Error as error:
            print(f"Failed to insert record into {table_name}" + " table {}".format(error))
            sys.exit()
        
        finally:    
            return assay_plate_insert_data(cursor, time_index, new_data, Data_information, Is_Test)
  



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

            # Recieving plate_id back to utilize the unique plate id in the assay_plate records
            plate_id = cursor.lastrowid

            # Considering the plate format, creating a given number of records in the assay_plate table
            row_num = 1
            create_empty_records_assay_plate(plate_id, cursor, row_num, num_wells, Is_Test)


    except mysql.connector.Error as error:
        print(f"Failed to insert record into {table_name}" + " table {}".format(error))
        sys.exit()

    except Exception as err:
        print("Is_Test invalid input!!! True for test tables, False for experiment tables")    

    else:
        print(num_plates, f" records inserted succesfully into {table_name} table")
        print(num_plates * num_wells, " records inserted succesfully into Assay_Plate table")
        
    finally:
        # Disconnect from the test_bugs database
        disconnect_Database(cursor, cnx)
        print("Connection to the database is closed")
        
def check_previous_data(cursor, plate_id, Is_Test):
    p_data = False 

    if Is_Test.lower() == "true":
        table_name = "Test_assay_plate"
    elif Is_Test.lower() == "false":
        table_name = "assay_plate"

    data_query = "Select Raw_Value from " + table_name + " WHERE plate_id = " + str(plate_id)
    # values = (plate_id)

    cursor.execute(data_query)
    data = cursor.fetchall()[-1][0]
    print(data)
    if data == None or data.upper() == "NULL":
        p_data = False
    else:
        p_data = True

    return p_data

#-----------------------------------------------
#-----------------------------------------------
def update_plate_data(experiment_name: str, plate_number: int, time_stamps: list, new_data: DataFrame, date: str, time: str, file_basename_for_data: str):
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
            
    """
    try:
        cursor,cnx = connect_Database() 
       
        # Find the plate_id for the given data
        experiment_name = experiment_name.strip()
        plate_id, table_name = plate_id_finder(cursor, experiment_name, plate_number)
        
        
        if plate_id == -1:
            print("Plate record does not exists in the database!!!")
            print("Creating new records for", experiment_name, " Barcode: 0")
            upload_data_directly(experiment_name, plate_number, time_stamps, new_data, date, time, file_basename_for_data)
        
        else:

            if table_name == "Test_plate":
                Is_Test = "true"
    
            elif table_name == "plate":
                Is_Test = "false"
                
            # Find format of the plate
            format = find_format(cursor, plate_id, Is_Test)
            
            # Counting how many records exist in the table. Returns the last index number
            row_num = count_rows_assay_table(cursor, plate_id, Is_Test) 

            # Checking if the database needs to be extended
            previous_data = check_previous_data(cursor,plate_id, Is_Test) 

            if previous_data:
                first_row_num = row_num + 1
                for lenght_time_stamps in range(len(time_stamps)):
                    row_num = create_empty_records_assay_plate(plate_id, cursor, row_num +1, format, Is_Test)


            if len(time_stamps) * format > row_num:
                # Creating new empty record in the assay_table until len(time_stamps) * format = row_num
                for lenght_time_stamps in range(len(time_stamps)-1):
                    row_num = create_empty_records_assay_plate(plate_id, cursor, row_num +1, format, Is_Test)

            if previous_data:
                row_num, data_index_num = first_row_num, 0 
            else:
                row_num, data_index_num = 1, 0

            # Update the records in the assay_plate table with the given data
            Data_information = [row_num, data_index_num, file_basename_for_data, date, time, plate_id]
            timestamp_tracker(time_stamps, cursor, new_data, Data_information, Is_Test)

            # Update plate info for the given plate_id and the timestemp


            update_plate_table = "UPDATE " + table_name + " SET Process_status = %s WHERE plate_id = %s"
            update_values = ("Completed", plate_id)
            cursor.execute(update_plate_table, update_values)
            
    
    except mysql.connector.Error as error:
        print("Failed to insert record into Test_assay_plate table {}".format(error))
        sys.exit()
    
    else:
        print(len(time_stamps)*len(new_data), "Records are inserted. Barcode:", plate_number)
    
    finally:
        # Disconnect from the test_bugs database
        disconnect_Database(cursor, cnx)        
        print("Connection to the database is closed")
   
            

#-----------------------------------------------
def upload_data_directly(experiment_name, plate_number, time_stamps, new_data, date, time, file_basename_for_data):
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
            
    """
    try:
        cursor,cnx = connect_Database()    

        add_plate = "INSERT INTO Test_plate (Type, Process_status, Barcode, Exp_ID, Format, Date_created, Time_created) VALUES (%s, %s, %s, %s, %s, %s, %s)"

        # Using the current time to keep track of the time when the plate information is recorded in the database 
        now = datetime.now()
        current_date = now.strftime("%Y-%m-%d")
        current_time = now.strftime("%H:%M:%S.%f")
                    
        plate_data = ("Hidex", "Completed", str(plate_number), experiment_name, 96, current_date, current_time)
        cursor.execute(add_plate, plate_data)
            
        # Recieving plate_id back to utilize the unique plate id in the assay_plate records
        plate_id = cursor.lastrowid
        
        row_num = 1
        for index in time_stamps:
            for data_index_num in range(1,len(new_data)+1):

                if new_data['Well'][data_index_num][0] == 'H':
                    Data_group = "Control"
                else:
                    Data_group = "Experimental"
                
                update_assay_plate = "INSERT INTO Test_assay_plate (plate_id, Data_group, Row_num, Well, Raw_Value, Elapsed_time, Data_File_Name, Reading_date, Reading_time, Assay_Details) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"                
                plate_assay_data = (plate_id, Data_group, row_num, new_data['Well'][data_index_num], new_data[index][data_index_num], index, file_basename_for_data, date, time, "Raw_OD(590)")
                cursor.execute(update_assay_plate, plate_assay_data)
                row_num+=1

    except mysql.connector.Error as error:
        print("Failed to insert record into Test_assay_plate table {}".format(error))
        sys.exit()

    finally:
        # Disconnect from the test_bugs database
        disconnect_Database(cursor, cnx)
        print("Connection to the database is closed")

#-----------------------------------------------
#Change the name of the fucntion LATER / Change column name control_qc
def insert_control_qc(experiment_name: str, plate_number: int, Control_QC: str):
    """update_z_core_qc

        Description: Enter Control_QC status into plate table for the given plate. 

        Parameters: 
            Control_QC: Either "Pass" or "Fail".
            plate_number: Plate id
            experiment_name: 
    """
    try:
        cursor,cnx = connect_Database()    

        plate_id, table_name = plate_id_finder(cursor, experiment_name, plate_number)

        
        update_plate_table = "UPDATE " + table_name + " SET Control_QC = %s WHERE plate_id = %s"
        update_values = (Control_QC, plate_id)
        cursor.execute(update_plate_table, update_values)

    except mysql.connector.Error as error:
        print(f"Failed to insert record into {table_name}" + " table {}".format(error))
    else: 
        print(f"Control_QC status inserted into {table_name} as ",Control_QC)
    finally:
        # Disconnect from the test_bugs database
        disconnect_Database(cursor, cnx)
        print("Connection to the database is closed")


#-----------------------------------------------
def insert_blank_adj(experiment_name, plate_number, adjusted_values_list):
    """insert_blank_adj

        Description: Inserts the blank adjusted values into assay_plate table
        Parameters: 
            experiment_name: 
            plate_number: Plate id
            blank_adj: A list that containes the blank adjusted values
            
    """
    try:
        cursor,cnx = connect_Database() 
        
        plate_id, table_name = plate_id_finder(cursor, experiment_name, plate_number)


        if table_name == "Test_plate":
            table_name = "Test_assay_plate"
        
        elif table_name == "plate":
            table_name = "assay_plate"
        
        for row_num, value in enumerate(adjusted_values_list):
            query = "UPDATE " + table_name + " SET Blank_Adj_Value = %s Where plate_id = %s and Row_num = %s"
            update_values = (value, plate_id, row_num+1)
            cursor.execute(query,update_values)
        

    except mysql.connector.Error as error:
        print("Faild to insert blank adjusted value into database {}".format(error))
    except Exception as err:
        print(err)
    else:
        print("Blank Adjusted values are inserted")
    finally:
        disconnect_Database(cursor,cnx)

#-----------------------------------------------
#blob_handler
def upload_image(filename, experiment_name: str, plate_number: int):
    """upload_image

        Description: Converts image to BLOB and then inserts it to plate table
        Parameters: 
            filename: Path to the image file
            experiment_name: 
            plate_number: Plate id
            
    """
    try:
        file = open(filename, 'rb')
    except OSError as err:
        print(err)
        sys.exit()
    else:
        with file:
            binary_data = file.read()

    try:
        cursor,cnx = connect_Database() 
        
        plate_id, table_name = plate_id_finder(cursor, experiment_name, plate_number)
        
        if table_name[0] == "T":
            table = "Test_graphs"
        elif table_name[0] == "p":
            table = "graphs"
        else:
            return
        
        Image_query =  "INSERT INTO " + table + " (exp_id, plate_id, exp_image) VALUES (%s, %s, %s)"
        update_values = (experiment_name, plate_number, binary_data)
        cursor.execute(Image_query, update_values)

    except mysql.connector.Error as error:
        print("Faild to insert image into database {}".format(error))
    except Exception as err:
        print(err)
    else:
        print("Image is inserted into plate table")
    finally:
        disconnect_Database(cursor,cnx)
        
#-----------------------------------------------
def retrieve_image(experiment_name: str, plate_number: int):
    """retrieve_image

    Description: Retrives blob from database, converts it to an image and saves to predefined directory
    Parameters: 
        experiment_name: 
        plate_number: Plate id
    """

    try:
        cursor,cnx = connect_Database() 
        
        plate_id, table_name = plate_id_finder(cursor, experiment_name, plate_number)


        if table_name[0] == "T":
            table = "Test_graphs"
        elif table_name[0] == "p":
            table = "graphs"
        else:
            return
        

        Image_query = "SELECT exp_image from " + table + " WHERE exp_id = %s and plate_id = %s"
        values = (experiment_name, plate_number)

        cursor.execute(Image_query, values)
        data = cursor.fetchone()[0]
        
        try:
            file = open("experiment_graph" + ".png", 'wb')
        except OSError as err:
            print(err)
            sys.exit()
        else:   
            with file:
                file.write(data)       
      

    except mysql.connector.Error as error:
        print("Faild to insert image into database {}".format(error))
    except Exception as err:
        print(err)
    else:
        print("Image retrieved")
    finally:
        disconnect_Database(cursor,cnx)
    
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

def parse_source_data(file):
    df = pd.DataFrame()
    DATA = False
    with open(file, newline="") as csvfile:
        print(f"opened {file}")
        csv.QUOTE_NONNUMERIC = True
        reader = csv.reader(csvfile)
        i = 0
        for row in reader:
            i += 1
            row = [x.strip() for x in row]
            if i == 1:
                name = row[0].strip()
            elif i == 2:
                date = row[0].strip()
            elif i == 3:
                plate_id = row[0].strip()

            if len(row) > 0 and row[0] == "Well":
                
                df = pd.DataFrame(columns=row)
                DATA = True
                continue
            if DATA == True:
                df.loc[len(df.index) + 1] = row
    #date = datetime.strptime(date, '%m/%d/%y').strftime('%Y-%m-%d')
    return df, name, date, plate_id

def insert_source_plate(file):

    df, name, date, plate_id = parse_source_data(file)
    try:
        cursor,cnx = connect_Database()    
        add_plate = "INSERT INTO plate (Type, Barcode, Exp_ID, Date_created) VALUES (%s, %s, %s, %s)"
        plate_data = ("Source", plate_id, name, date)
        cursor.execute(add_plate, plate_data)

            
        # Recieving plate_id back to utilize the unique plate id in the assay_plate records
        plate_id = cursor.lastrowid

        for data in range(1, len(df)+1):
            update_assay_plate = "INSERT INTO source_plate (plate_id, well, sample_id) VALUES (%s, %s, %s)"                
            plate_assay_data = (plate_id, df['Well'][data].strip(), df['Sample ID'][data].strip())
            cursor.execute(update_assay_plate, plate_assay_data)
           

    except mysql.connector.Error as error:
        print("Failed to insert record {}".format(error))
        sys.exit()

    finally:
        # Disconnect from the test_bugs database
        disconnect_Database(cursor, cnx)
        print("Connection to the database is closed")


    
# Currently not in use
def add_time(date, time, time_stamp):
    
    date = date.split("-", 3)
    time = time.split(":",3)
    date_and_time = datetime.datetime(int(date[0]), int(date[1]), int(date[2]), int(time[0]), int(time[1]), int(time[2]))
    print(date_and_time)
    pass

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
    
def main(filename):
    df, date_time  = parse_hidex(filename)
    time_stamps = df.columns[3:].to_list()
    date_time = date_time.split(" ", 1)
    # print(df)
    # blank_adj = {'A1': 0.5319999999999999, 'A2': 0.7965, 'A3': 1.091, 'A4': 1.1945, 'A5': 1.2455, 'A6': 1.402, 'A7': 0.5389999999999999, 'A8': 0.7595000000000001, 'A9': 1.097, 'A10': 1.2274999999999998, 'A11': 1.2255, 'A12': 1.3739999999999999, 'B1': 0.599, 'B2': 0.8635, 'B3': 1.135, 'B4': 1.2414999999999998, 'B5': 1.3445, 'B6': 1.48, 'B7': 0.6479999999999999, 'B8': 0.8985, 'B9': 1.1260000000000001, 'B10': 1.2334999999999998, 'B11': 1.3185, 'B12': 1.4589999999999999, 'C1': 0.48900000000000005, 'C2': 0.6875, 'C3': 0.9939999999999999, 'C4': 1.1864999999999999, 'C5': 1.2785, 'C6': 1.458, 'C7': 0.5549999999999999, 'C8': 0.7885, 'C9': 0.95, 'C10': 1.2094999999999998, 'C11': 1.2315, 'C12': 1.445, 'D1': 0.388, 'D2': 0.6455, 'D3': 0.8069999999999999, 'D4': 0.9105, 'D5': 1.0415, 'D6': 1.156, 'D7': 0.391, 'D8': 0.6365000000000001, 'D9': 0.7989999999999999, 'D10': 0.9175, 'D11': 0.9984999999999999, 'D12': 1.193, 'E1': 1.126, 'E2': 1.3485, 'E3': 1.383, 'E4': 1.3555, 'E5': 1.3615, 'E6': 1.349, 'E7': 1.379, 'E8': 1.3355, 'E9': 1.374, 'E10': 1.3375, 'E11': 1.3125, 'E12': 1.27, 'F1': 0.45, 'F2': 0.7085, 'F3': 1.107, 'F4': 1.2834999999999999, 'F5': 1.3835, 'F6': 1.4989999999999999, 'F7': 0.691, 'F8': 0.9225, 'F9': 1.1560000000000001, 'F10': 1.2945, 'F11': 1.2945, 'F12': 1.466, 'G1': 0.508, 'G2': 0.7005, 'G3': 1.01, 'G4': 1.1875, 'G5': 1.3665, 'G6': 1.4829999999999999, 'G7': 0.76, 'G8': 0.9155, 'G9': 1.1260000000000001, 'G10': 1.2445, 'G11': 1.3025, 'G12': 1.438, 'H1': 0.0010000000000000009, 'H2': 0.0005000000000000004, 'H3': 0.0020000000000000018, 'H4': 0.0, 'H5': 0.0, 'H6': 0.0, 'H7': 0.0, 'H8': 0.0, 'H9': 0.0, 'H10': 0.0005000000000000004, 'H11': 0.0005000000000000004, 'H12': 0.0010000000000000009}
    Is_Test = "True"
    # print(blank_list)
    #insert_source_plate('/homes/dozgulbas/data/11_17_21_plate2.csv')
    # Calling the create empty plate records function.
    # create_empty_plate_records(1, 48, "Hidex", "Campaign1_20210505_191201_RawOD.csv", Is_Test)
    
    # create_empty_plate_records(4, 96, "Hidex", "Campaign2-loop-v1-1665690122", Is_Test)


    
    # Calling the update plate data function
    
    update_plate_data("Campaign2-loop-v1-1665690122", 3, time_stamps, df, date_time[0], date_time[1], "Campaign1_noIncubate2_20221014_043915_RawOD.csv")

    #calling blob handler function
    # upload_image('/homes/dozgulbas/hudson-liquidhandling/rdbms/images/Campaign2_HopeStrains127-133_plate2col7_12hrInc_12PlateTest.png',filename, 0)
    
    # retrieve_image(filename, 0)


    # insert_control_qc(filename, 0,"Pass")
    
    # df1, blank_list = od_blank_adjusted(df, time_stamps)

    # insert_blank_adj("Campaign1_20210505_191201_RawOD.csv", 0, blank_adj)
    # insert_blank_adj(filename, 0, blank_list)

if __name__ == "__main__":
    #Execute only if run as a script
    # main('/lambda_stor/data/hudson/data/1623878974-1/Campaign1_20210615_150156_RawOD.csv')
    # main("/lambda_stor/data/hudson/data/1620252337-1/Campaign1_20210505_144922_RawOD.csv")
    main("/homes/dozgulbas/hudson-liquidhandling/rdbms/test_data/Campaign1_noIncubate2_20221014_043915_RawOD.csv")

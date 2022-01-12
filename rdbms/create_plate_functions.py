import sys
import os
import csv
from connect import connect
from datetime import datetime

# Function to connect to the test_bugs database
def connect_Database():

    cnx = connect()
    cursor = cnx.cursor()
    # start transaction
    cursor.execute("SET autocommit = 0")
    cursor.execute("START TRANSACTION")
    return cursor,cnx

#Function to disconnect from the test_bugs database
def disconnect_Database(cursor,cnx):

    cursor.execute("COMMIT")
    cursor.execute("SET autocommit = 1")
    cursor.close()
    cnx.close()

# Function creates empty records in the "plate" and "assay_plate" tables, considering the given plate information.
def create_empty_plate_records(num_plates, num_wells, plate_type, directory_name):    

    # Connect to the test_bugs database
    cursor,cnx = connect_Database()    
    
    # A list that keeps the Plate IDs
    plate_id = []
    curr = 0

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
        plate_id.append(cursor.lastrowid) 

        # Considering the plate format, creating a given number of records in the assay_plate table 
        for records in range(0, num_wells):
            
            #Create empty assay_plate row
            add_assay_plate = """INSERT INTO assay_plate (plate_id, RawOD_590)
                               VALUES (%s, %s)"""
    
            assay_data = (plate_id[curr],"RawOD")
            cursor.execute(add_assay_plate, assay_data)

        curr += 1
    
    # Disconnect from the test_bugs database
    disconnect_Database(cursor,cnx)
    
    # Function returns the list of Plate IDs that are created in the database
    return plate_id

# Function to update the records for the given plate. Accepts the data file, plate id that is going to be updated and the reading time 
def update_plate_data(new_data, plate_id, timestemp):
    #connect to the test_bugs database
    cursor,cnx = connect_Database() 
    
    # Update plate info for the given plate_id and the timestemp
    update_plate = "UPDATE plate SET process_status = %s WHERE plate_id = %s"
    update_values = ("completed", plate_id)
    
    cursor.execute(update_plate,update_values)
    
    # Update the records in the assay_plate table with the given data
    curr = 0
    for row in new_data:
        update_assay_plate = "UPDATE assay_plate SET well=%s, sample=%s, value=%s WHERE plate_id = %s AND create_time = %s"
        plate_assay_data = (row[0], row[1], row[3], plate_id, timestemp[curr])
        curr +=1
        cursor.execute(update_assay_plate, plate_assay_data)

    
    #Disconnect from the test_bugs database
    disconnect_Database(cursor,cnx)


#-----------------------------------------------

#TEST if this is a plate with the info below. 
# plate_info = (6, 10, "directory_name", "plate_type")

#TODO: Read plate info from the dictionary
#num_plates, num_wells, exp_id, plate_type = dic.get('num_plates'), dic.get('num_wells'), dic.get('directory_name'), dic.get('plate_type')
#plate_info = (num_plates, num_wells, exp_id, plate_type)

# Calling the create empty plate records function. Function returns a list of recently created Plate IDs
plate_id_list = create_empty_plate_records(plate_info)


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




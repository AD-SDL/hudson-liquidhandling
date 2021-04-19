import sys
import os
import csv
from connect import connect

# Test data at rdbms/data/Campaign1_hidex1_04-07-21.tsv

cnx = connect()
cursor = cnx.cursor()

# start transaction
cursor.execute("SET autocommit = 0")
cursor.execute("START TRANSACTION")

# assume the name of the file is the barcode
barcode = os.path.basename(sys.argv[1])

add_plate = "INSERT INTO plate (type, process_status, barcode, format) VALUES ('assay','complete', '" + barcode + "', '96')"
cursor.execute(add_plate)
plate_id = cursor.lastrowid

add_assay_plate = ("INSERT INTO assay_plate (plate_id, type, well, sample, value) "
        "VALUES (%s, %s, %s, %s, %s)")
data_file = open(sys.argv[1])
reader = csv.reader(data_file, delimiter="\t")
for row in reader:
    if row[0].lower() == 'well':
        continue
    plate_assay_data = (plate_id, 'hidex', row[0], row[1], row[3])
    cursor.execute(add_assay_plate, plate_assay_data) 

# comit transaction
cursor.execute("COMMIT")
cursor.execute("SET autocommit = 1")
cnx.close()

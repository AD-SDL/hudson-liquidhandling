import sys
import os
import csv
from connect import connect


cnx = connect()
cursor = cnx.cursor()
cursor.execute("SET autocommit = 0")
cursor.execute("START TRANSACTION")

# execute your query
cursor.execute("delete from plate;")
tables = cursor.fetchall()
print("All records are deleted from Plate table")
cursor.execute("delete from assay_plate;")
tables = cursor.fetchall()
print("All records are deleted from Assay_Plate table")

cursor.execute("COMMIT")
cursor.execute("SET autocommit = 1")
cursor.close()
cnx.close()
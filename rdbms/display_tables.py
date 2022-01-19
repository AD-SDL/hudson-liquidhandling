import sys
import os
import csv
from connect import connect



cnx = connect()
cursor = cnx.cursor()
cursor.execute("SET autocommit = 0")
cursor.execute("START TRANSACTION")

# execute your query
cursor.execute("select * from plate;")
tables = cursor.fetchall()
print(tables)

cursor.execute("select * from assay_plate;")
tables = cursor.fetchall()
print(tables)

cursor.execute("COMMIT")
cursor.execute("SET autocommit = 1")
cursor.close()
cnx.close()


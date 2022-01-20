import sys
import os
import csv
from connect import connect



cnx = connect()
cursor = cnx.cursor()
cursor.execute("SET autocommit = 0")
cursor.execute("START TRANSACTION")
cursor.execute("desc plate;")
tables = cursor.fetchall()
print(tables)
# execute your query
cursor.execute("select * from plate;")
tables = cursor.fetchall()
for k in range(len(tables)):
    print(tables[k])

cursor.execute("desc assay_plate;")
tables = cursor.fetchall()
print(tables)
cursor.execute("select * from assay_plate;")
tables = cursor.fetchall()
for k in range(len(tables)):
    print(tables[k])

cursor.execute("COMMIT")
cursor.execute("SET autocommit = 1")
cursor.close()
cnx.close()


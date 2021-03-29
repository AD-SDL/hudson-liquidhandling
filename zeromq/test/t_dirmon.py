from dirmon import checkDir
import time

# check for files that were modified in the last 10 minutes

t = 600
new_files = checkDir(".", last_mtime=t)

for f in new_files:
    print ("new file {}".format(f))

import sys
from dirmon import checkDir

dir = sys.argv[1]
last_mtime = int(sys.argv[2])

new_files=[]
processed_files=[]

while(1):
	new_files = checkDir(dir, last_mtime)
	if len(new_files) > 0:
		for filename in new_files:
			if filename in processed_files: continue
			print("spawn run_qc.py {}".format(filename))
			processed_files.append(filename)
		new_files = []

	# sleep last_mtime - 
	print(processed_files)
	print ("resuming")


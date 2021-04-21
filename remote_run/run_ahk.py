# CHECKS BEFORE AUTOMATIC REMOTE RUN
# - check that no process is currently running
# - check that a new manifest file was added to instructions folder
# - check that most recent manifest file is not already listed in the RUN_LOG
# - check that all required files listed in manifest are present
# open the associated .ahk file if all good to go

# TODO figure out how to kill unwanted processes if they are already running

""" The WMI portion of this code is from:
https://www.geeksforgeeks.org/python-get-list-of-running-processes/#:~:text=We%20would%20be%20using%20the%20WMI.,and%20stored%20in%20variable%20process.
"""

import os
import wmi
import glob
from datetime import date, datetime
import time

f = wmi.WMI()  # initialize windows management instrumentation

# * Program variables
instructions_folder_path = "C:\\labautomation\\instructions"
is_already_running = False
process_names = ["SOLOSoft.exe", "SoftLinxVProtocolEditor.exe"]  # SLinx.exe
all_files_present = False
present_in_log = False
created_recently = False
most_recent_txt_path = (
    None  # path of most recent manifest file in labautomation\instuctions folder
)
most_recent_txt_timestamp = None
most_recent_ahk_path = None
run_log_filename = instructions_folder_path + "\\RUN_LOG.txt"

# print timestamp to log file
# time.sleep(5)
print(str(date.today()) + " " + str(datetime.now().time()))

# * Check currently running processes for SoloSoft or SoftLinx .exe files
for process in f.Win32_Process():
    if process.Name in process_names:
        is_already_running = True
        print("Process already running, cannot open .ahk file")
        print("\t" + f"{process.ProcessId:<10}  {process.Name}" + str(date.today()))

# * Find most recent manifest file
list_of_txt_files = glob.glob(
    instructions_folder_path + "\\*.txt"
)  # list of all .txt files

max_timestamp = 0
if not len(list_of_txt_files) == 0:
    for txt_file in list_of_txt_files:
        with open(txt_file) as f:
            first_line = f.readline().strip()
            try:  # is manifest file iff first line is timestamp
                timestamp = float(first_line)
                if timestamp > max_timestamp:  # save most recent manifest details
                    max_timestamp = timestamp
                    most_recent_txt_path = txt_file
            except ValueError:
                print("The file run is not a manifest file")
    # save timestamp if there is a most recent manifest file
    if not max_timestamp == 0:
        most_recent_txt_timestamp = max_timestamp
else:
    print("There are no .txt files in the labautomation instructions folder.")

# * Manifest File Checks -> created within last 20 minutes AND all required files in instructions folder
if most_recent_txt_path:
    # check that manifest was created recently enough (within the last hour?)
    if time.time() - 3600 <= most_recent_txt_timestamp:
        created_recently = True
    else:
        print("Most recent manifest file was not created in the last hour.")

    # check RUN_LOG.txt for record of most recent manifest file, if present don't run
    if os.path.exists(run_log_filename):
        print("RUN_LOG.txt exists in the labautomation/instructions folder")
        with open(run_log_filename, "r") as run_log:
            for log_line in run_log:
                log_line_filename = log_line.split(", ")[0].strip()
                log_line_timestamp = log_line.split(", ")[1].strip()
                if (str(log_line_filename) == str(most_recent_txt_path)) and (
                    str(log_line_timestamp) == str(most_recent_txt_timestamp)
                ):
                    present_in_log = True
                    break  # stop searching log file once match found
    else:
        print("No RUN_LOG found. A new one will be created.")

    if (
        present_in_log == False
    ):  # only if protocol is not present in log (not already run)
        # check that all required files are present
        with open(most_recent_txt_path) as f:
            required_files_list = f.readlines()[2:]
            required_files_list = [
                each.strip() for each in required_files_list
            ]  # remove newline character

            file_present = ""  # store status of each file in instructions folder (1=present, 0=absent)
            for i in range(len(required_files_list)):
                file_path_to_check = f.name.replace(
                    os.path.basename(f.name), required_files_list[i]
                )
                if os.path.exists(file_path_to_check):
                    file_present += "1"
                    if file_path_to_check.endswith(".ahk"):  # save the .ahk file path
                        most_recent_ahk_path = file_path_to_check
                else:
                    file_present += "0"
                    print(
                        "A required file is missing: " + os.path.basename(f.name)
                    )  # will print to log file

            # check that all files are present and flip the boolean
            if not "0" in file_present:
                all_files_present = True
                print("All required files are present.")
    else:
        print("Most recent manifest file was already run (record found in RUN_LOG.txt)")
else:
    print("No recent manifest file in instructions folder")

# * Run .ahk file if everything is good to go
if (
    created_recently and all_files_present and not is_already_running
):  # ok becuase all files present only can be true only iff not present in log file
    os.startfile(most_recent_ahk_path)
    print("The .ahk file was opened.")

    # add name of manifest file and timestamp to run log
    # add human readable timestamp as well?
    with open(run_log_filename, "a+") as run_log:
        run_log.write(
            most_recent_txt_path + ", " + str(most_recent_txt_timestamp) + "\n"
        )

else:
    print("Not running .ahk file")

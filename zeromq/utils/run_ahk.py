import os
import wmi
from datetime import date, datetime
import time


def run_ahk(instructions_dir_path):  # new instructions folder path

    print("run_ahk.py called on instructions: deciding if ok to run ahk")

    # save name of instructions directory
    if os.path.exists(os.path.dirname(instructions_dir_path)):
        dir_base_name = os.path.basename(os.path.dirname(instructions_dir_path))

    # * Program Variables
    process_names = ["SOLOSoft.exe", "SoftLinxVProtocolEditor.exe"]  # SLinx.exe
    is_already_running = False
    all_files_present = False
    present_in_log = False

    manifest = None
    ahk_file = None

    hudson01_instruction_dir = os.path.split(os.path.dirname(instructions_dir_path))[0]
    hudson01_log_dir_path = os.path.join(hudson01_instruction_dir, "log/")
    run_log_path = os.path.join(hudson01_log_dir_path, "RUN_LOG.txt")
    error_log_path = os.path.join(hudson01_log_dir_path, "ERROR_LOG.txt")

    # * Create log folder & log files (if don't already exist)
    # Log directory
    if not os.path.exists(os.path.dirname(hudson01_log_dir_path)):
        try:
            os.makedirs(os.path.dirname(hudson01_log_dir_path))
        except OSError as exc:
            print("Failed to create directory-> " + str(hudson01_log_dir_path))
            raise

    # Log files (RUN_LOG and ERROR_LOG)
    run_log = open(run_log_path, "a+")
    error_log = open(error_log_path, "a+")

    # write message address to RUN_LOG and ERROR_LOG
    run_log.write(dir_base_name + "\n")
    run_log.write("\t" + str(time.time()) + ", " + str(datetime.now()) + "\n")
    error_log.write(dir_base_name + "\n")
    error_log.write("\t" + str(time.time()) + ", " + str(datetime.now()) + "\n")

    # * Check that SoloSoft and SoftLinx are not already running
    print("checking if SoloSoft or SoftLinx is already running")
    f = wmi.WMI()
    for process in f.Win32_Process():
        if process.Name in process_names:
            is_already_running = True
            error_log.write("\tProcess already running, cannot open .ahk file\n")
            error_log.write(
                "\t\t"
                + f"{process.ProcessId:<10}  {process.Name}"
                + str(date.today())
                + "\n"
            )

    # * Check that RUN_LOG does not already contain record of these instructions (have not been run before)
    with open(run_log_path) as read_run_log:
        run_log_contents = [line.strip() for line in read_run_log.readlines()]
        if dir_base_name in run_log_contents:
            present_in_log = True
            error_log.write("\tCurrent instructions folder has already been run\n")

    if not present_in_log:
        # locate the manifest file
        instruction_txt_files = [
            os.path.join(instructions_dir_path, f)
            for f in os.listdir(instructions_dir_path)
            if str(f).endswith(".txt")
        ]
        for txt_file_path in instruction_txt_files:
            with open(txt_file_path, "r") as open_txt_file:
                first_line = open_txt_file.readline().strip()
                try:
                    timestamp = float(
                        first_line
                    )  # manifest will have timestamp on first line
                    manifest = txt_file_path
                except ValueError as e:
                    error_log.write(
                        f"\t{os.path.basename(txt_file_path)} is not a manifest file\n"
                    )

        # extract list of required files from manifest
        if manifest:

            with open(manifest, "r") as open_manifest:
                # skips over the first two timestamp lines of manifest
                required_files = [l.strip() for l in open_manifest.readlines()][2:]

                # make sure all required files are present
                file_status = ""
                for each in required_files:
                    if each in os.listdir(os.path.dirname(instructions_dir_path)):
                        file_status += "1"
                    else:
                        error_log.write(f"\tRequired file not present: {each}\n")
                        file_status += "0"

                    # locate the AutoHotKey script
                    if each.endswith(".ahk"):
                        ahk_file = each
                        ahk_path = os.path.join(instructions_dir_path, ahk_file)

                if not "0" in file_status:
                    all_files_present = True
                    run_log.write("\tAll required files are present\n")
        else:
            error_log.write("\tManifest file not found\n")

    # * Run .ahk file if everything is good to go
    if ahk_file and all_files_present and not is_already_running and not present_in_log:
        try:
            # os.startfile(ahk_path) # WORKS
            run_log.write(
                f"\tSUCCESS. The .ahk file was opened ({ahk_path}), protocol executed in SoftLinx\n"
            )
            error_log.write("\tNO ERRORS\n")
            print(f"NO ERRORS, will run ahk path {ahk_path}")
        except OSError as e:
            print(e)
            error_log.write(f"\tERROR: could not open ahk file. {e}\n")
            run_log.write("\tFAILURE: ahk file not opened\n")
    else:
        run_log.write("\tDid not start protocol\n")

    # * Close log files
    run_log.close()
    error_log.close()

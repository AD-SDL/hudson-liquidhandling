import argparse
import os
import sys
import time
from subprocess import Popen
from liquidhandling import SoloSoft
from liquidhandling import SoftLinx
from liquidhandling import DeepBlock_96VWR_75870_792_sterile
from liquidhandling import Reservoir_12col_Agilent_201256_100_BATSgroup
from liquidhandling import Plate_96_Corning_3635_ClearUVAssay


def test():
    lambda6_path = "/lambda_stor/data/hudson/instructions/"
    num_assay_plates = 1
    num_assay_wells = 96
    assay_plate_type = "hidex"
    is_test = False
    return_val = "PASS"
    project = "test_shutoff"
    project_desc = "loop"
    version_num = "v1"
    timestamp = str(time.time()).split(".")[0]
    directory_name = f"{project}-{project_desc}-{version_num}-{timestamp}"
    directory_path = os.path.join(
        os.path.realpath(os.path.dirname(lambda6_path)), directory_name
    )
    print(f"Protocol directory created: {directory_path}")

    try:
        os.makedirs(directory_path, exist_ok=True)
    except OSError as e:
        print(e)
        print(f"failed to create new directory for instructions: {directory_path}")

    softLinx = SoftLinx("test_shutoff", os.path.join(directory_path, "test_shutoff.slvp"))
    softLinx.plateCraneMoveCrane("SoftLinx.PlateCrane.LidNest2")
    softLinx.plateCraneMoveCrane("SoftLinx.PlateCrane.Safe")
    softLinx.runProgram("C:\\Users\\svcaibio\\Dev\\liquidhandling\\kill_process.bat")
    softLinx.saveProtocol()

    try:
        # TODO: change to full path on lambda6
        child_message_sender = child_pid = Popen(
            [
                "python",
                "../../zeromq/lambda6_send_instructions.py",
                "-d",
                directory_path,
                "-i", 
                str(num_assay_plates),
                str(num_assay_wells),
                assay_plate_type,
                str(is_test),
            ],
            start_new_session=True,
        ).pid
        print("New instruction directory passed to lambda6_send_message.py")
    except Error as e:
        print(e)
        print("Could not send new instructions to hudson01")

    return return_val




def main():
    test()




if __name__ == "__main__":
    # execute only if run as a script
    main()
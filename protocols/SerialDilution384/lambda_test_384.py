import argparse
from multiprocessing import pool
import os
import sys
import time
from subprocess import Popen
from liquidhandling import SoloSoft
from liquidhandling import SoftLinx
from liquidhandling import DeepBlock_96VWR_75870_792_sterile
from liquidhandling import Reservoir_12col_Agilent_201256_100_BATSgroup
from liquidhandling import Plate_96_Corning_3635_ClearUVAssay
from tip_utils import replace_tip_box, remove_tip_box
from campaign2_loop_dil2x_384_multiple_treatments_functions import *

def generate_test_repeatable():
    return_val = "PASS"
    lambda6_path = "/lambda_stor/data/hudson/instructions/"

    project = "SerialDil384"
    project_desc = "loop"
    version_num = "384"
    timestamp = str(time.time()).split(".")[0]
    directory_name = f"{project}-{project_desc}-{version_num}-{timestamp}"
    directory_path = os.path.join(
        os.path.realpath(os.path.dirname(lambda6_path)), directory_name
    )

    num_assay_plates = 4 # from cl args
    num_assay_wells = 384  # hardcoded for now
    assay_plate_type = "hidex"

    # * create new directory to hold new instructions
    try:
        os.makedirs(directory_path, exist_ok=True)
        print(f"Protocol directory created: {directory_path}")
    except OSError as e:
        print(e)
        print(f"failed to create new directory for instructions: {directory_path}")

    
    # initialize softLinx
    softLinx = SoftLinx("Steps_384_assay_multi_treatment", os.path.join(directory_path, "steps384_assay_multi_treatment.slvp"))

    softLinx.setPlates(
        {"SoftLinx.PlateCrane.Stack5": "Plate.96.Corning-3635.ClearUVAssay"}
    )

    # set up equiptment
    softLinx.hidexRun("SetTemp37")
    softLinx.liconicBeginShake(shaker1Speed=30)


    softLinx.plateCraneMovePlate(
            ["SoftLinx.PlateCrane.Stack5"], ["SoftLinx.Solo.Position4"], hasLid=True, poolID=5
        )
    
    softLinx.plateCraneRemoveLid(
            ["SoftLinx.Solo.Position4"], ["SoftLinx.PlateCrane.LidNest2"]
        )
    

    softLinx.plateCraneMovePlate(["SoftLinx.Solo.Position4"], ["SoftLinx.Hidex.Nest"])
    softLinx.hidexClose()
    softLinx.plateCraneMoveCrane("SoftLinx.PlateCrane.Safe")
    softLinx.hidexRun("Campaign1_noIncubate2_384")

    # lambda6 TODO
    softLinx.runProgram(
    "C:\\Users\\svcaibio\\Dev\\liquidhandling\\zeromq\\utils\\send_data.bat", arguments=f"{1} {directory_name} serial_dilution"
    )

    # Move plate back to incubator, replace lid
    softLinx.plateCraneMovePlate(["SoftLinx.Hidex.Nest"], ["SoftLinx.Liconic.Nest"])
    softLinx.hidexClose()
    softLinx.plateCraneReplaceLid(["SoftLinx.PlateCrane.LidNest2"], ["SoftLinx.Liconic.Nest"])
    softLinx.plateCraneMoveCrane("SoftLinx.PlateCrane.Safe")
    softLinx.liconicLoadIncubator(loadID=1, holdWithoutIncubationTime=True)


    softLinx.liconicShake(shaker1Speed=30, shakeTime=[0,0,0,10]) # 1 hour

    softLinx.plateCraneMoveCrane("SoftLinx.PlateCrane.Safe")

    softLinx.liconicUnloadIncubator(loadID=1)


    softLinx.hidexRun("SetTemp20")
    softLinx.liconicEndShake()


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
                str(False),
            ],
            start_new_session=True,
        ).pid

        print("New instruction directory passed to lambda6_send_message.py")
    except BaseException as e:
        print(e)
        print("Could not send new instructions to hudson01")
    
def main():
    # parser = argparse.ArgumentParser()

    generate_test_repeatable()


if __name__ == "__main__":
    # execute only if run as a script
    main()
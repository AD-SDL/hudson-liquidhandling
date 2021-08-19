import argparse
import os
import sys
import time
from subprocess import Popen
from liquidhandling import SoloSoft
from liquidhandling import SoftLinx

def read_OD590(plate_id, directory_path):

    
    # SoftLinx Protocol--------------------------------------------------------------
    softLinx = SoftLinx(f"Absorbance {plate_id}", os.path.join(directory_path, f"Absorbance_{plate_id}.slvp"))

    # define starting plate layout
    softLinx.setPlates(
        {"SoftLinx.Solo.Position4": "Plate.96.Corning-3635.ClearUVAssay"}
    )

    softLinx.plateCraneMovePlate(["SoftLinx.Solo.Position4"], ["SoftLinx.Solo.Position4"])

    # remove plate lid and place on temp Lid Nest 2
    softLinx.plateCraneRemoveLid(["SoftLinx.Solo.Position4"], ["SoftLinx.PlateCrane.LidNest2"])

    # move growth plate to Hidex
    softLinx.plateCraneMovePlate(
        ["SoftLinx.Solo.Position4"], ["SoftLinx.Hidex.Nest"]
    )  # no need to open hidex
    softLinx.hidexClose()
    softLinx.plateCraneMoveCrane("SoftLinx.PlateCrane.Safe")

    # Run Hidex Protocol
    softLinx.hidexRun("Campaign1_noIncubate2")   

    # move growth plate to Hidex
    softLinx.plateCraneMovePlate(
        ["SoftLinx.Hidex.Nest"], ["SoftLinx.PlateCrane.LidNest1"]
    )  # no need to open hidex

    # close the Hidex
    softLinx.hidexClose()

    # replace lid 
    softLinx.plateCraneReplaceLid(["SoftLinx.PlateCrane.LidNest2"], ["SoftLinx.PlateCrane.LidNest1"])

    softLinx.plateCraneMoveCrane("SoftLinx.PlateCrane.Safe")

    #send the data to lambda6
    softLinx.runProgram(
        "C:\\Users\\svcaibio\\Dev\\liquidhandling\\protocols\\campaign1\\send_OD590.bat"
    )

    # generate the SoftLinx files
    softLinx.saveProtocol()


def main(args):
    # Parse args
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-id",
        "--plate_id",
        help="id of the plate being placed into the hidex",
        required=True,
        type=str,
    )
    
    args = vars(parser.parse_args())

    # * Create folder to store all instruction files ---------------------------------
    local_path = "C:\\labautomation\\PeptideData\\ReadOD590_Instructions\\"
    project = "Campaign1"
    project_desc = "Arvind"
    plate_id = args["plate_id"]
    #timestamp = str(time.time()).split(".")[0]
    directory_name = f"{project}-{project_desc}-{plate_id}"
    directory_path = os.path.join(
        os.path.realpath(os.path.dirname(local_path)), directory_name
    )
    print(f"Protocol directory created: {directory_path}")

    # * create new directory to hold new instructions
    try:
        os.makedirs(directory_path, exist_ok=True)
    except OSError as e:
        print(e)
        print(f"failed to create new directory for instructions: {directory_path}")
    # pass to method
    read_OD590(plate_id=plate_id, directory_path=directory_path)

    # run ahk file 
    ahk_basename = f"Absorbance_{plate_id}.ahk"
    ahk_filename = os.path.join(directory_path, ahk_basename)
    print("Running the following ahk file in 5 seconds: ")
    print(f"\t{ahk_filename}")

    # sleep for 5 seconds then run the ahk file 
    time.sleep(5)
    os.startfile(ahk_filename)

if __name__ == "__main__":
    # execute only if run as a script
    main(sys.argv)
    # time.sleep(5)
    # os.open(ahk_filename)


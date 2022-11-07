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
from tip_utils import replace_tip_box, remove_tip_box

def test():
    directory_path = "C:\\Users\\svcaibio\\Dev\\liquidhandling\\protocols\\test"
    softLinx = SoftLinx("peel_test", os.path.join(directory_path, "peel_test.slvp"))

    softLinx.runProgram("C:\\Users\\svcaibio\\Dev\\liquidhandling\\peel_plate.bat", arguments=f"{4} {2.5}" )
    softLinx.liconicShake(30, 30, [0, 0, 0, 30])
    softLinx.plateCraneMoveCrane("SoftLinx.PlateCrane.LidNest1")
    softLinx.plateCraneMoveCrane("SoftLinx.PlateCrane.Safe")
    softLinx.saveProtocol()

def main():

    # # initialize softLinx
    # softLinx = SoftLinx("peel_test", os.path.join(directory_path, "peel_test.slvp"))
    # softLinx.runProgram("C:\Users\svcaibio\Dev\liquidhandling\peel_plate.bat", arguments=f"{4}{2.5}" )
    # # softLinx.runProgram(
    # #         "C:\\Users\\svcaibio\\Dev\\liquidhandling\\zeromq\\utils\\send_data.bat", arguments=f"{k} {directory_name} campaign2"
    # #     )
    test()

if __name__ == "__main__":

    main()
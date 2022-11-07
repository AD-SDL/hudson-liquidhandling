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
    softLinx = SoftLinx("seal_test", os.path.join(directory_path, "seal_test.slvp"))

    softLinx.runProgram("C:\\Users\\svcaibio\\Dev\\liquidhandling\\seal_plate.bat", arguments=f"{175} {3.0}" )
    softLinx.liconicShake(30, 30, [0, 0, 0, 30])
    softLinx.plateCraneMoveCrane("SoftLinx.PlateCrane.LidNest1")
    softLinx.plateCraneMoveCrane("SoftLinx.PlateCrane.Safe")
    softLinx.saveProtocol()

def main():

    test()

if __name__ == "__main__":

    main()
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
    dir_path = "C:\\Users\\svcaibio\\Dev\\liquidhandling\\protocols\\campaign2\\test_hso"
    softLinx = SoftLinx("kill_test", os.path.join(dir_path, "kill_test.slvp"))
    softLinx.plateCraneMoveCrane("SoftLinx.PlateCrane.Safe")
    softLinx.plateCraneMoveCrane("SoftLinx.PlateCrane.LidNest1")
    softLinx.plateCraneMoveCrane("SoftLinx.PlateCrane.Safe")
    softLinx.runProgram(
            "C:\\Users\\svcaibio\\Dev\\liquidhandling\\kill_process.bat"
        )
    softLinx.saveProtocol()

def main():
    test()

if __name__ == "__main__":
    # execute only if run as a script
    main()
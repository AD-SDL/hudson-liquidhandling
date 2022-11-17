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



    # * Initialize soloSoft (step 1)
    step1_hso_filename = os.path.join(dir_path, f"plate{1}_step1.hso")
    
    soloSoft = SoloSoft(
        filename=step1_hso_filename,
        plateList=[
            "DeepBlock.96.VWR-75870-792.sterile",
            "Empty",
            "TipBox.180uL.Axygen-EVF-180-R-S.bluebox",
            "Plate.96.Corning-3635.ClearUVAssay",
            "Empty",
            "Empty",
            "Empty",
            "Empty",
        ],
    )

    # * Fill all columns of empty 96 well plate (corning 3383 or Falcon - ref 353916) with fresh lb media (12 channel in Position 3, media_start_column and media_start_column+1)
    soloSoft.getTip("Position3")  
    j = 1
    for i in range(1, 7):  # first half plate = media from column 1
        soloSoft.aspirate(
            position="Position1",
            aspirate_volumes=Reservoir_12col_Agilent_201256_100_BATSgroup().setColumn(
                1, 30
            ),
            aspirate_shift=[0, 0, 0.5],
        )
        soloSoft.dispense(
            position="Position4",
            dispense_volumes=Plate_96_Corning_3635_ClearUVAssay().setColumn(
                i, 30
            ),
            dispense_shift=[0, 0, 0.5],
        )

    for i in range(7, 13):  # second half plate = media from column 2
        soloSoft.aspirate(
            position="Position1",
            aspirate_volumes=Reservoir_12col_Agilent_201256_100_BATSgroup().setColumn(
                2, 30
            ),
            aspirate_shift=[0, 0, 0.5],
        )
        soloSoft.dispense(
            position="Position4",
            dispense_volumes=Plate_96_Corning_3635_ClearUVAssay().setColumn(
                i, 30
            ),
            dispense_shift=[0, 0, 0.5],
        )
    soloSoft.shuckTip()
    soloSoft.savePipeline()



    softLinx = SoftLinx("demo", os.path.join(dir_path, "demo.slvp"))
    softLinx.setPlates(
        {"SoftLinx.PlateCrane.Stack5": "Plate.96.Corning-3635.ClearUVAssay", 
        "SoftLinx.PlateCrane.Stack4": "TipBox.180uL.Axygen-EVF-180-R-S.bluebox"}
    )
    softLinx.hidexRun("SetTemp37")
    softLinx.liconicBeginShake(shaker1Speed=30)

    softLinx.plateCraneMovePlate(
            ["SoftLinx.PlateCrane.Stack5"], ["SoftLinx.Solo.Position4"], hasLid=True
        )
    # remove lid and place in Lid Nest
    softLinx.plateCraneRemoveLid(
        ["SoftLinx.Solo.Position4"], ["SoftLinx.PlateCrane.LidNest2"]
    )

    replace_tip_box(softLinx, "Position3") 
    softLinx.soloSoftResetTipCount(3)

    softLinx.plateCraneMoveCrane("SoftLinx.PlateCrane.Safe")

    softLinx.soloSoftRun(
            dir_path
            + "\\"
            + os.path.basename(step1_hso_filename)
        )

    softLinx.plateCraneMovePlate(
            ["SoftLinx.Solo.Position4"], ["SoftLinx.Hidex.Nest"]
        )  # no need to open hidex
    softLinx.hidexClose()
    softLinx.plateCraneMoveCrane("SoftLinx.PlateCrane.Safe")
    softLinx.hidexRun("Campaign1_noIncubate2") 
   
    # Transfer plate to Liconic.Nest and replace lid
    softLinx.plateCraneMovePlate(["SoftLinx.Hidex.Nest"], ["SoftLinx.Liconic.Nest"])
    #softLinx.plateCraneMovePlate(["SoftLinx.Solo.Position4"], ["SoftLinx.Liconic.Nest"])
    softLinx.hidexClose()
    softLinx.plateCraneReplaceLid(["SoftLinx.PlateCrane.LidNest2"], ["SoftLinx.Liconic.Nest"])
    softLinx.plateCraneMoveCrane("SoftLinx.PlateCrane.Safe")

    # Load plate into incubator
    softLinx.liconicLoadIncubator(loadID=1, holdWithoutIncubationTime=True)  
    softLinx.hidexRun("SetTemp20") 
    softLinx.liconicEndShake()
    
    # save protocol to write instructions to .slvp file, create .txt manifest, and .ahk remote start file
    softLinx.saveProtocol()


def main():
    test()

if __name__ == "__main__":
    # execute only if run as a script
    main()
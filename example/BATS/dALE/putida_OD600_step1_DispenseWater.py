""" 
Putida.OD600.step2.DispenseWater

Steps: 
- Transfer 180uL water from 12 Channel Reservoir - Column 1 to Corning 3635 - Columns 1-6
- Transfer 180 uL water from 12 Channel Reservoir - Column 2 to Corning 3635 - Columns 7-12


Deck Layout:
1 -> TipBox-Corning 200uL (orange)
2 -> Empty (HEATING NEST)
3 -> 12 Channel Reservoir (Water -> C1,2; Buffer -> C7,8)
4 -> Round Bottom Storage
5 -> Deep Block 96 well
6 -> Corning 3635 Clear UV 96 well
7 -> Empty
8 -> Empty

"""
import os
import sys
from liquidhandling import SoloSoft
from liquidhandling import SoftLinx
from liquidhandling import (
    Reservoir_12col_Agilent_201256_100_BATSgroup,
    Plate_96_Corning_3635_ClearUVAssay,
)

# Program Variables
transfer_volume = 180
blowoff_volume = 10

soloSoft = SoloSoft(
    filename="putida_OD600_step1_DispenseWater.hso",
    plateList=[
        "TipBox.200uL.Corning-4864.orangebox",
        "Empty",
        "Reservoir.12col.Agilent-201256-100.BATSgroup",
        "Plate.96.Agilent-5043-9310.RoundBottomStorage",
        "DeepBlock.96.VWR-75870-792.sterile",
        "Plate.96.Corning-3635.ClearUVAssay",
        "Empty",
        "Empty",
    ],
)

soloSoft.getTip()

for i in range(1, 3):  # columns in 12 channel reservoir
    for j in range(1, 7):  # <- columns in corning 3635 clearUV
        soloSoft.aspirate(
            position="Position3",
            aspirate_volumes=Reservoir_12col_Agilent_201256_100_BATSgroup().setColumn(
                i, transfer_volume
            ),
            aspirate_shift=[
                0,
                0,
                4,
            ],  # larger shift needed for 12 channel resevoir <- check this with new plate entries
            pre_aspirate=blowoff_volume,
        )
        soloSoft.dispense(
            position="Position6",
            dispense_volumes=Plate_96_Corning_3635_ClearUVAssay().setColumn(
                (((i - 1) * 6) + j), transfer_volume
            ),
            dispense_shift=[0, 0, 2],
            blowoff=blowoff_volume,
        )

soloSoft.shuckTip()
soloSoft.savePipeline()

# UNCOMMENT FOLLOWING CODE TO GENERATE SOFTLINX .AHK FILE FOR THIS STEP ALONE

softLinx = SoftLinx(
    "Putida.OD600.step1.DispenseWater", "putida_OD600_step1_DispenseWater.slvp"
)
softLinx.soloSoftRun(
    "C:\\Users\\svcaibio\\Dev\\liquidhandling\\example\\BATS\\dALE\\putida_OD600_step1_DispenseWater.hso"
)
softLinx.saveProtocol()

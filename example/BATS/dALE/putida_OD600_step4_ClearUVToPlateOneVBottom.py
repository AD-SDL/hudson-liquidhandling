""" 
Putida.OD600.step4.TransferToRoundBottom

Steps: 
- Transfer all contents of wells in ClearUV plate (used for Hidex) to PlateOne V Bottom for centrifugation
    - ok if bubbles -> centrifuge should take care of them

Deck Layout:
1 -> TipBox-Corning 200uL (orange)
2 -> Empty (HEATING NEST)
3 -> 12 Channel Reservoir (Water -> C1,2; Buffer -> C7,8)
4 -> Round Bottom Storage
5 -> Deep Block 96 well
6 -> Corning 3635 Clear UV 96 well
7 -> PlateOne V Bottom
8 -> Empty

"""
import os
import sys
from liquidhandling import SoloSoft
from liquidhandling import *

# Program Variables
transfer_volume = 150
blowoff_volume = 0
clearance_from_bottom = 1

soloSoft = SoloSoft(
    filename="putida_OD600_step4_ClearUVToPlateOneVBottom.hso",
    plateList=[
        "TipBox.200uL.Corning-4864.orangebox",
        "Empty",
        "Reservoir.12col.Agilent-201256-100.BATSgroup",
        "Plate.96.Agilent-5043-9310.RoundBottomStorage",
        "DeepBlock.96.VWR-75870-792.sterile",
        "Plate.96.Corning-3635.ClearUVAssay",
        "Plate.96.PlateOne-1833-9600.ConicalBottomStorage",
        "Empty",
    ],
)


for i in range(1, 13):  # i = 1,2,..., 12
    soloSoft.getTip()  # need to get new tips every time
    soloSoft.aspirate(
        position="Position6",
        aspirate_volumes=Plate_96_Corning_3635_ClearUVAssay().setColumn(
            i, transfer_volume
        ),
        aspirate_shift=[0, 0, clearance_from_bottom],
        pre_aspirate=blowoff_volume,
    )
    soloSoft.dispense(
        position="Position7",
        dispense_volumes=Plate_96_PlateOne_1833_9600_ConicalBottomStorage().setColumn(
            i, transfer_volume
        ),
        dispense_shift=[0, 0, clearance_from_bottom],
        blowoff=blowoff_volume,
    )

soloSoft.shuckTip()
soloSoft.savePipeline()

# UNCOMMENT FOLLOWING CODE TO GENERATE SOFTLINX .AHK FILE FOR THIS STEP ALONE

softLinx = SoftLinx(
    "Putida.OD600.step4.ClearUVToPlateOneVBottom",
    "putida_OD600_step4_ClearUVToPlateOneVBottom.slvp",
)
softLinx.soloSoftRun(
    "C:\\Users\\svcaibio\\Dev\\liquidhandling\\example\\BATS\\dALE\\putida_OD600_step4_ClearUVToPlateOneVBottom.hso"
)
softLinx.saveProtocol()
""" 
Putida.OD600.step4.TransferToRoundBottom

Steps: 
- Transfer 20uL supernatant from PlateOneVBottom - Columns 1-12 to Round Bottom Storage - Columns 1-12 
    - make sure to keep 2mm clearance from the bottom and add x and y offset during aspirate step

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
transfer_volume = 20
blowoff_volume = 10
aspirate_x_shift = 2
aspirate_y_shift = 2
aspirate_z_shift = 2
dispense_z_shift = 2


soloSoft = SoloSoft(
    filename="putida_OD600_step5_TransferToRoundBottom.hso",
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
        position="Position7",
        aspirate_volumes=Plate_96_PlateOne_1833_9600_ConicalBottomStorage().setColumn(
            i, transfer_volume
        ),
        aspirate_shift=[aspirate_x_shift, aspirate_y_shift, aspirate_z_shift],
        pre_aspirate=blowoff_volume,
    )
    soloSoft.dispense(
        position="Position4",
        dispense_volumes=Plate_96_Agilent_5043_9310_RoundBottomStorage().setColumn(
            i, transfer_volume
        ),
        dispense_shift=[0, 0, dispense_z_shift],
        blowoff=blowoff_volume,
    )

soloSoft.shuckTip()
soloSoft.savePipeline()

# UNCOMMENT FOLLOWING CODE TO GENERATE SOFTLINX .AHK FILE FOR THIS STEP ALONE

softLinx = SoftLinx(
    "Putida.OD600.step5.TransferToRoundBottom",
    "putida_OD600_step5_TransferToRoundBottom.slvp",
)
softLinx.soloSoftRun(
    "C:\\Users\\svcaibio\\Dev\\liquidhandling\\example\\BATS\\dALE\\putida_OD600_step5_TransferToRoundBottom.hso"
)
softLinx.saveProtocol()

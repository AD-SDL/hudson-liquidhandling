""" 
Putida.OD600.step3.DispenseBuffer

Steps: 
- Transfer 180uL buffer from 12 Channel Reservoir - Column 7 to Round Bottom Storage - Columns 1-6
- Transfer 180uL buffer from 12 Channel Reservoir - Column 8 to Round Bottom Storage - Columns 7-12

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
from liquidhandling import *

# Program Variables
transfer_volume = 180 
blowoff_volume = 10

soloSoft = SoloSoft(
    filename="putida_OD600_step3_DispenseBuffer.hso",
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

for i in range(7,9): # columns in 12 channel reservoir
    for j in range(1,7):  # <- columns in round bottom storage 
        soloSoft.aspirate(
            position="Position3",
            aspirate_volumes=Reservoir_12col_Agilent_201256_100_BATSgroup().setColumn(i,transfer_volume), 
            aspirate_shift=[0,0,4], # larger shift needed for 12 channel resevoir <- check this with new plate entries
            pre_aspirate=blowoff_volume, 
        )
        soloSoft.dispense(
            position="Position4",
            dispense_volumes=Plate_96_Agilent_5043_9310_RoundBottomStorage().setColumn((((i-7)*6)+j), transfer_volume), 
            dispense_shift=[0,0,2],
            blowoff=blowoff_volume,
        )
soloSoft.shuckTip()
soloSoft.savePipeline()

# UNCOMMENT FOLLOWING CODE TO GENERATE SOFTLINX .AHK FILE FOR THIS STEP ALONE

softLinx = SoftLinx("Putida.OD600.step3.DispenseBuffer", "putida_OD600_step3_DispenseBuffer.slvp")
softLinx.soloSoftRun( "C:\\Users\\svcaibio\\Dev\\liquidhandling\\example\\BATS\\dALE\\putida_OD600_step3_DispenseBuffer.hso")
softLinx.saveProtocol()

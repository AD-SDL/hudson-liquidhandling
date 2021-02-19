""" 
Putida.OD600.step2.TransferBacteria

Steps: 
- Transfer 20uL bacterial suspension from Deep Block - Columns 1-12 to Corning 3635 - Columns 1-12  
    - use 200uL tips 
    - keep 3 mm clearance from the bottom 

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
transfer_volume = 20 
blowoff_volume = 10
clearance_from_bottom = 3

soloSoft = SoloSoft(
    filename="putida_OD600_step2_TransferBacteria.hso",
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

for i in range(1,13): # i = 1,2,..., 12
    soloSoft.getTip()  # need to get new tips every time -> assumes wells in bacterial suspension not all the same
    soloSoft.aspirate(
        position="Position5", 
        aspirate_volumes=DeepBlock_96VWR_75870_792_sterile().setColumn(i, transfer_volume),
        aspirate_shift=[0,0,clearance_from_bottom], 
        pre_aspirate=blowoff_volume,
    )
    soloSoft.dispense(
        position="Position6", 
        dispense_volumes=Plate_96_Corning_3635_ClearUVAssay().setColumn(i, transfer_volume), 
        dispense_shift=[0,0,clearance_from_bottom], 
        blowoff=blowoff_volume,
    )

soloSoft.shuckTip()
soloSoft.savePipeline()

# UNCOMMENT FOLLOWING CODE TO GENERATE SOFTLINX .AHK FILE FOR THIS STEP ALONE

softLinx = SoftLinx("Putida.OD600.step2.TransferBacteria", "putida_OD600_step2_TransferBacteria.slvp")
softLinx.soloSoftRun( "C:\\Users\\svcaibio\\Dev\\liquidhandling\\example\\BATS\\dALE\\putida_OD600_step2_TransferBacteria.hso")
softLinx.saveProtocol()
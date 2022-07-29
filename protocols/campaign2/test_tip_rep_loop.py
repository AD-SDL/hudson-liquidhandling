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

# initialize softLinx
softLinx = SoftLinx("TestTipRepLoop", "C:\\Users\\svcaibio\\Desktop\\Debug\\TestTipRepLoop.slvp")

# define starting plate layout
softLinx.setPlates(
    {"SoftLinx.PlateCrane.Stack5": "Plate.96.Corning-3635.ClearUVAssay", 
    "SoftLinx.PlateCrane.Stack4": "TipBox.180uL.Axygen-EVF-180-R-S.bluebox"}
)

for k in range(12): 
    # move plate from stack 1 to stack 5
    softLinx.plateCraneMovePlate(["SoftLinx.PlateCrane.Stack5"], ["SoftLinx.PlateCrane.Stack1"], hasLid=True)
    print("Picking up Test plate")
    softLinx.plateCraneMoveCrane()
    if k < 6:
        print("Picking up tip box")
        softLinx.plateCraneMovePlate(["SoftLinx.PlateCrane.Stack4"], ["SoftLinx.PlateCrane.Stack3"], hasLid=True)
        softLinx.plateCraneMoveCrane()

    

# for k in range(12): 
#     # replace tip box if necessary
#     if (k%2 == 0):
#         if k == 0: 
#             replace_tip_box(softLinx, "Position3") 
#         else: 
#             remove_tip_box(softLinx, "Position3")
#             replace_tip_box(softLinx, "Position3")
#         #softLinx.soloSoftResetTipCount(1)  # Reset the tip count every other run. 

#     softLinx.plateCraneMoveCrane("SoftLinx.PlateCrane.Safe")

#     softLinx.liconicShake(shaker1Speed=30, shakeTime=[0,0,0,10])  # shake for 10 seconds for testing

softLinx.saveProtocol()
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

softLinx = SoftLinx("IncubatorTest", "C:\\Users\\svcaibio\\Desktop\\Debug\\StackTest.slvp")

# # define starting plate layout
# # softLinx.setPlates(
# #     {"SoftLinx.PlateCrane.Stack5": "Plate.96.Corning-3635.ClearUVAssay"}
# # )
# softLinx.setPlates(
#     {"SoftLinx.PlateCrane.Stack5": "TestPlate.96"}
# )

# for i in range(12):
#     softLinx.plateCraneMovePlate(
#     ["SoftLinx.PlateCrane.Stack5"], ["SoftLinx.Solo.Position4"], hasLid=True)
#     softLinx.plateCraneMovePlate(
#         ["SoftLinx.Solo.Position4"], ["SoftLinx.PlateCrane.Stack1"], hasLid=True
#     )

k = 5 
# softLinx.plateCraneMoveCrane("SoftLinx.PlateCrane.Safe")
softLinx.runProgram(
    "C:\\Users\\svcaibio\\Dev\\liquidhandling\\zeromq\\utils\\send_data.bat", arguments=f"{k} TEST_PROTOCOL_NAME")
softLinx.saveProtocol()



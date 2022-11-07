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

softLinx = SoftLinx("IncubatorTest", "C:\\Users\\svcaibio\\Desktop\\Debug\\IncubatorTest.slvp")

# define starting plate layout
softLinx.setPlates(
    {"SoftLinx.PlateCrane.Stack5": "Plate.96.Corning-3635.ClearUVAssay"}
)

# preheat Hidex to 37 for timepoint 0 reading
softLinx.hidexRun("SetTemp37")

# restock growth assay plate before run
softLinx.plateCraneMovePlate(
    ["SoftLinx.PlateCrane.Stack5"], ["SoftLinx.Solo.Position4"]
)
# remove lid and place in Lid Nest
softLinx.plateCraneRemoveLid(
    ["SoftLinx.Solo.Position4"], ["SoftLinx.PlateCrane.LidNest2"]
)
softLinx.plateCraneMoveCrane("SoftLinx.PlateCrane.Safe")
 
    # DON'T DO THIS IFINCUBATING ONE PLATE IN HIDEX
    #replace the lid
    #softLinx.plateCraneReplaceLid(["SoftLinx.PlateCrane.LidNest2"], ["SoftLinx.Solo.Position4"])

    # # move growth plate to Temp deck (This is where the plate would be moved to the incubator)
    # softLinx.plateCraneMovePlate(
    #     ["SoftLinx.Solo.Position4"], ["SoftLinx.PlateCrane.LidNest1"]
    # )  # no need to open hidex

# transfer plate to Hidex (take timepoint 0 reading)
softLinx.plateCraneMovePlate(
    ["SoftLinx.Solo.Position4"], ["SoftLinx.Hidex.Nest"]
)  # no need to open hidex
softLinx.hidexClose()
softLinx.plateCraneMoveCrane("SoftLinx.PlateCrane.Safe")

# Run Hidex Protocol (this will close the Hidex)
softLinx.hidexRun("Campaign1_noIncubate2")  # only one reading

# Transfer Hidex data (timepoint 0 data)
# softLinx.runProgram(
#     "C:\\Users\\svcaibio\\Dev\\liquidhandling\\zeromq\\utils\\send_data.bat"
# )

# Transfer plate to Liconic.Nest and replace lid
softLinx.plateCraneMovePlate(["SoftLinx.Hidex.Nest"], ["SoftLinx.Liconic.Nest"])
softLinx.hidexClose()
softLinx.plateCraneReplaceLid(["SoftLinx.PlateCrane.LidNest2"], ["SoftLinx.Liconic.Nest"])
softLinx.plateCraneMoveCrane("SoftLinx.PlateCrane.Safe")

# set Hidex Temperature back to 20 deg C
softLinx.hidexRun("SetTemp20")

# Load plate into incubator and begin timed shake
softLinx.liconicLoadIncubator(loadID=1, holdWithoutIncubationTime=True)  # shake for 16 hours ([days, hours, minutes, seconds])
softLinx.liconicShake(shaker1Speed=30, shakeTime=[0,0,0,30])  # 30 second incubation for testing

# Preheat Hidex to take reading (could also do this earlier...)
softLinx.hidexRun("SetTempWait37")  # waits for Hidex to heat to 37

# Transfer plate from incubator to Hidex and take endpoint reading
softLinx.liconicUnloadIncubator(loadID=1)
softLinx.plateCraneRemoveLid(["SoftLinx.Liconic.Nest"], ["SoftLinx.PlateCrane.LidNest2"])
softLinx.plateCraneMovePlate(["SoftLinx.Liconic.Nest"], ["SoftLinx.Hidex.Nest"])
softLinx.hidexClose()
softLinx.plateCraneMoveCrane("SoftLinx.PlateCrane.Safe")
softLinx.hidexRun("Campaign1_noIncubate2")

# transfer data to lambda6
# softLinx.runProgram(
#     "C:\\Users\\svcaibio\\Dev\\liquidhandling\\zeromq\\utils\\send_data.bat"
# )

# Move plate from Hidex to LidNest1 and replace lid
softLinx.plateCraneMovePlate(["SoftLinx.Hidex.Nest"], ["SoftLinx.PlateCrane.LidNest1AfterHidex"])
softLinx.hidexClose()
softLinx.plateCraneReplaceLid(["SoftLinx.PlateCrane.LidNest2"], ["SoftLinx.PlateCrane.LidNest1"])
softLinx.plateCraneMoveCrane("SoftLinx.PlateCrane.Safe")


# save protocol to write instructions to .slvp file, create .txt manifest, and .ahk remote start file
softLinx.saveProtocol()


# STEPS FOR INCUBATOR TESTING
# softLinx.setPlates({"SoftLinx.Liconic.Nest": "Plate.96.Corning-3635.ClearUVAssay"})

# softLinx.liconicLoadIncubator(loadID=1, holdWithoutIncubationTime=True)
# #softLinx.liconicBeginShake(shaker1Speed=20, shaker2Speed=30)
# #softLinx.liconicEndShake(shaker="both")
# softLinx.liconicShake(shaker1Speed=30, shaker2Speed=20, shakeTime=[0,0,0,20])
# softLinx.liconicUnloadIncubator(loadID=1)

# softLinx.saveProtocol()


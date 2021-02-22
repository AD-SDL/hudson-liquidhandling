"""
This file generates one softLinx .ahk file for Putida.OD600 steps 1 and 3  
    (just in case you want to run both dispense steps at the same time)

Can also be used to run all 4 steps at the same time -> just uncomment steps 2 and 4 below
"""
import os
import sys
from liquidhandling import SoloSoft
from liquidhandling import SoftLinx
from liquidhandling import Reservoir_12col_Agilent_201256_100_BATSgroup, Plate_96_Corning_3635_ClearUVAssay

# do we need to initialize this if we aren't creating a soloSoft.hso within this python file?
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
# Force steps 1-4 to run individually so that all .hso files are created
os.popen('python ./putida_OD600_step1_DispenseWater.py')
#os.popen('python ./putida_OD600_step2_TransferBacteria.py')
os.popen('python ./putida_OD600_step3_DispenseBuffer.py')
#os.popen('python ./putida_OD600_step4_TransferToRoundBottom.py')

# in itialize softLinx and add all .hso files to the softLinx protocol
softLinx = SoftLinx("Putida.OD600.steps1to4_softLinx", "putida_OD600_steps1to4_softLinx.slvp")
# add step 1
softLinx.soloSoftRun( "C:\\Users\\svcaibio\\Dev\\liquidhandling\\example\\BATS\\dALE\\putida_OD600_step1_DispenseWater.hso")
# add step 2
#softLinx.soloSoftRun( "C:\\Users\\svcaibio\\Dev\\liquidhandling\\example\\BATS\\dALE\\putida_OD600_step2_TransferBacteria.hso")
# add step 3
softLinx.soloSoftRun( "C:\\Users\\svcaibio\\Dev\\liquidhandling\\example\\BATS\\dALE\\putida_OD600_step3_DispenseBuffer.hso")
# add step 4
#softLinx.soloSoftRun( "C:\\Users\\svcaibio\\Dev\\liquidhandling\\example\\BATS\\dALE\\putida_OD600_step4_TransferToRoundBottom.hso")

# generate .slvp and .ahk files
softLinx.saveProtocol()


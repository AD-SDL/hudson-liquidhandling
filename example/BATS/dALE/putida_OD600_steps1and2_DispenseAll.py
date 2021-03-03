"""
This file combines...
    Putida_OD600_DispenseWater.py 
    Putida_OD600_DispenseBuffer.py
... into the same .hso file to make dispensing steps faster

"""
import os
import sys
from liquidhandling import SoloSoft
from liquidhandling import SoftLinx
from liquidhandling import (
    Reservoir_12col_Agilent_201256_100_BATSgroup,
    Plate_96_Corning_3635_ClearUVAssay,
    Plate_96_Agilent_5043_9310_RoundBottomStorage,
)

soloSoft = SoloSoft(
    filename="putida_OD600_steps1and2_DispenseAll.hso",
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

# * DISPENSE WATER ------------------------------------------

# Program Variables
transfer_volume = 180
blowoff_volume = 10

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

# DISPENSE BUFFER ------------------------------------------

# Program Variables
transfer_volume = 180
blowoff_volume = 10

soloSoft.getTip()
for i in range(7, 9):  # columns in 12 channel reservoir
    for j in range(1, 7):  # <- columns in round bottom storage
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
            position="Position4",
            dispense_volumes=Plate_96_Agilent_5043_9310_RoundBottomStorage().setColumn(
                (((i - 7) * 6) + j), transfer_volume
            ),
            dispense_shift=[0, 0, 2],
            blowoff=blowoff_volume,
        )

soloSoft.shuckTip()
soloSoft.savePipeline()

softLinx = SoftLinx(
    "Putida.OD600.Steps1and2.DispenseAll", "putida.OD600.Steps1and2.DispenseAll.slvp"
)
softLinx.soloSoftRun(
    "C:\\Users\\svcaibio\\Dev\\liquidhandling\\example\\BATS\\dALE\\putida_OD600_steps1and2_DispenseAll.hso"
)
softLinx.saveProtocol()


# # Force steps 1-4 to run individually so that all .hso files are created
# os.popen("python ./putida_OD600_DispenseWater.py")
# # os.popen('python ./putida_OD600_step2_TransferBacteria.py')
# os.popen("python ./putida_OD600_DispenseBuffer.py")
# # os.popen('python ./putida_OD600_step4_TransferToRoundBottom.py')

# # in itialize softLinx and add all .hso files to the softLinx protocol
# softLinx = SoftLinx(
#     "Putida.OD600.steps1and2.DispenseAll", "putida_OD600_steps1and2_DispenseAll.slvp"
# )
# # add step 1
# softLinx.soloSoftRun(
#     "C:\\Users\\svcaibio\\Dev\\liquidhandling\\example\\BATS\\dALE\\putida_OD600_DispenseWater.hso"
# )
# # add step 2
# # softLinx.soloSoftRun( "C:\\Users\\svcaibio\\Dev\\liquidhandling\\example\\BATS\\dALE\\putida_OD600_step2_TransferBacteria.hso")
# # add step 3
# softLinx.soloSoftRun(
#     "C:\\Users\\svcaibio\\Dev\\liquidhandling\\example\\BATS\\dALE\\putida_OD600_DispenseBuffer.hso"
# )
# # add step 4
# # softLinx.soloSoftRun( "C:\\Users\\svcaibio\\Dev\\liquidhandling\\example\\BATS\\dALE\\putida_OD600_step4_TransferToRoundBottom.hso")

# # generate .slvp and .ahk files
# softLinx.saveProtocol()

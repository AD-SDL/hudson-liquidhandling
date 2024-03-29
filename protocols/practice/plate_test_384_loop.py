# TODO: Test this

from liquidhandling import SoftLinx, SoloSoft
from liquidhandling import *

# * Program Variables
trans_volume = 10
default_z_shift = 0.5

# * Initialize Solo
soloSoft = SoloSoft(
    filename="plate_test_384.hso",
    plateList=[
        "Empty",
        "Empty",
        "Empty",
        "Empty",
        "Empty",
        "Empty",
        "TipBox.50uL.Axygen-EV-50-R-S.tealbox",
        "Plate.384.Corning-3540.BlackwClearBottomAssay",
    ],
)

soloSoft.getTip("Position7")
# * aspirate/dispense column 1, rows A C E G I K M O  (odd rows) -> start A1
j = 1
for i in range(1,7):

    soloSoft.aspirate(
        position="Position8",
        aspirate_volumes=Plate_384_Corning_3540_BlackwClearBottomAssay().setColumn(
            1, trans_volume
        ),
        aspirate_shift=[0, 0, default_z_shift],
    )
    soloSoft.dispense(
        position="Position8",
        dispense_volumes=Plate_384_Corning_3540_BlackwClearBottomAssay().setColumn(
            2, trans_volume
        ),
        dispense_shift=[0, 0, default_z_shift],
    )
aspirate_volumes_startB = Plate_384_Corning_3540_BlackwClearBottomAssay().setColumn(
    1, trans_volume
)
aspirate_volumes_startB[0][0] = 0


# * aspirate/dispense column 1, rows B D F H J L N P (even rows) -> start B1
# change value in first row to 0 -> shortcut to make soloSoft start at Row B
# TODO: Add an easier way to accomplish this
j = 1
for j in range (1,7):
    soloSoft.aspirate(
        position="Position8",
        aspirate_volumes=aspirate_volumes_startB,
        aspirate_shift=[0, 0, default_z_shift],
    )

    dispense_volumes_startB = Plate_384_Corning_3540_BlackwClearBottomAssay().setColumn(
        2, trans_volume
    )
    dispense_volumes_startB[0][1] = 0
    soloSoft.dispense(
        position="Position8",
        dispense_volumes=dispense_volumes_startB,
        dispense_shift=[0, 0, default_z_shift],
    )

soloSoft.shuckTip()
soloSoft.savePipeline()

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
        "DeepBlock.96.VWR-75870-792.sterile",
        "Empty",
        "Empty",
        "Empty",
        "Empty",
        "Empty",
        "TipBox.50uL.Axygen-EV-50-R-S.tealbox",
        "Corning 3540",
    ],
)


# soloSoft.getTip("Position7")
# # * aspirate/dispense column 1, rows A C E G I K M O  (odd rows) -> start A1

# for i in range(1,3):

#     soloSoft.aspirate(
#         position="Position8",
#         aspirate_volumes=Plate_384_Corning_3540_BlackwClearBottomAssay().setColumn(
#             i, trans_volume
#         ),
#         aspirate_shift=[0, 0, default_z_shift],
#     )
#     soloSoft.dispense(
#         position="Position8",
#         dispense_volumes=Plate_384_Corning_3540_BlackwClearBottomAssay().setColumn(
#             i+1, trans_volume
#         ),
#         dispense_shift=[0, 0, default_z_shift],
#     )

# # * aspirate/dispense column 1, rows B D F H J L N P (even rows) -> start B1
# # change value in first row to 0 -> shortcut to make soloSoft start at Row B
# # TODO: Add an easier way to accomplish this



# for i in range(1,3):
#     aspirate_volumes_startB = Plate_384_Corning_3540_BlackwClearBottomAssay().setColumn(
#     i, trans_volume)
#     aspirate_volumes_startB[0][i-1] = 0

#     soloSoft.aspirate(
#         position="Position8",
#         aspirate_volumes=aspirate_volumes_startB,
#         aspirate_shift=[0, 0, default_z_shift],
#     )

#     dispense_volumes_startB = Plate_384_Corning_3540_BlackwClearBottomAssay().setColumn(
#         i+1, trans_volume
#     )
#     dispense_volumes_startB[0][i] = 0
#     soloSoft.dispense(
#         position="Position8",
#         dispense_volumes=dispense_volumes_startB,
#         dispense_shift=[0, 0, default_z_shift],
#     )

soloSoft.getTip("Position7")

for i in range(1, 7):  # first half plate = media from column 1
    # soloSoft.aspirate(
    #     position="Position1",
    #     aspirate_volumes=DeepBlock_96VWR_75870_792_sterile().setColumn(
    #         i, 10
    #     ),
    #     aspirate_shift=[0, 0, default_z_shift],
    # )
    # soloSoft.dispense(
    #     position="Position8",
    #     dispense_volumes=Plate_384_Corning_3540_BlackwClearBottomAssay().setColumn(
    #         i, 10
    #     ),
    #     dispense_shift=[0, 0, default_z_shift],
    # )

    soloSoft.aspirate(
        position="Position1",
        aspirate_volumes=DeepBlock_96VWR_75870_792_sterile().setColumn(
            1, 10
        ),
        aspirate_shift=[0, 0, default_z_shift],
    )
    dispense_volumes_startB = Plate_384_Corning_3540_BlackwClearBottomAssay().setColumn(
            6+i, 10
        )
    dispense_volumes_startB[0][i+5] = 0
    soloSoft.dispense(
        position="Position8",
        dispense_volumes= dispense_volumes_startB,
        dispense_shift=[0, 0, default_z_shift],
    )
           
soloSoft.shuckTip()
soloSoft.savePipeline()

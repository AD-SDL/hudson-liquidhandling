from liquidhandling import SoloSoft, SoftLinx
from liquidhandling import *  # replace with plate types used

# TipBox.50uL.Axygen-EV-50-R-S.tealbox
# TipBox.200uL.Corning-4864.orangebox
# Reservoir.12col.Agilent-201256-100.BATSgroup

# * Program Variables ------------------
initial_well_volume = 1000

asp_volume = 10
asp_z_shift = 0.5

# * ---------------------------------------
soloSoft = SoloSoft(
    filename="min_volume_z_shift_test.hso",
    plateList=[
        "Empty",
        "Empty",
        "Empty",
        "Empty",
        "Empty",
        "Empty",
        "TipBox.50uL.Axygen-EV-50-R-S.tealbox",
        "Plate.96.PlateOne-1833-9600.ConicalBottomStorage",
    ],
)
# soloSoft.getTip("Position7")
# for i in range(int(initial_well_volume/(asp_volume*8))+2):
#     soloSoft.aspirate(
#             position="Position8",
#             aspirate_volumes=Reservoir_12col_Agilent_201256_100_BATSgroup().setColumn(1, asp_volume),
#             aspirate_shift=[0,0,asp_z_shift],
#     )
#     soloSoft.dispense(
#         position="Position8",
#         dispense_volumes=Reservoir_12col_Agilent_201256_100_BATSgroup().setColumn(2, asp_volume),
#         dispense_shift=[0,0,asp_z_shift],
#     )

# * Campaign 1, Deep Block Column 1 Volume Test
# soloSoft.getTip("Position7")
# for i in range(6):
#     soloSoft.aspirate(
#             position="Position8",
#             aspirate_volumes=DeepBlock_96VWR_75870_792_sterile().setColumn(1, 60),
#             aspirate_shift=[0,0,asp_z_shift],
#     )
#     soloSoft.dispense(
#         position="Position8",
#         dispense_volumes=DeepBlock_96VWR_75870_792_sterile().setColumn(2, 60),
#         dispense_shift=[0,0,asp_z_shift],
#     )

# soloSoft.aspirate(
#         position="Position8",
#         aspirate_volumes=DeepBlock_96VWR_75870_792_sterile().setColumn(1, 198),
#         aspirate_shift=[0,0,asp_z_shift],
# )
# soloSoft.dispense(
#     position="Position8",
#     dispense_volumes=DeepBlock_96VWR_75870_792_sterile().setColumn(2, 198),
#     dispense_shift=[0,0,asp_z_shift],
# )

# for i in range(5):
#     soloSoft.aspirate(
#             position="Position8",
#             aspirate_volumes=DeepBlock_96VWR_75870_792_sterile().setColumn(1, 135),
#             aspirate_shift=[0,0,asp_z_shift],
#     )
#     soloSoft.dispense(
#         position="Position8",
#         dispense_volumes=DeepBlock_96VWR_75870_792_sterile().setColumn(2, 135),
#         dispense_shift=[0,0,asp_z_shift],
#     )

# #* Campaign 1, Deep block Column 2 and Culture Plate Volume Test
# soloSoft.getTip("Position7")
# soloSoft.aspirate(
#         position="Position8",
#         aspirate_volumes=DeepBlock_96VWR_75870_792_sterile().setColumn(1, 22),
#         aspirate_shift=[0,0,asp_z_shift],
# )
# soloSoft.dispense(
#     position="Position8",
#     dispense_volumes=DeepBlock_96VWR_75870_792_sterile().setColumn(2, 22),
#     dispense_shift=[0,0,asp_z_shift],
# )

# * Campaign 2, Day 1: 12 channel res columns 1,2 volume test
# soloSoft.getTip("Position7")
# for i in range(6):
#     soloSoft.aspirate(
#         position="Position8",
#         aspirate_volumes=Reservoir_12col_Agilent_201256_100_BATSgroup().setColumn(1, 180),
#         aspirate_shift=[0,0,asp_z_shift],
#     )
#     soloSoft.dispense(
#         position="Position8",
#         dispense_volumes=Reservoir_12col_Agilent_201256_100_BATSgroup().setColumn(2, 180),
#         dispense_shift=[0,0,asp_z_shift],
#     )

# * Campaign 2, Day 1 Conical Bottom Storage Volume Test

soloSoft.getTip("Position7")
soloSoft.aspirate(
    position="Position8",
    aspirate_volumes=Plate_96_PlateOne_1833_9600_ConicalBottomStorage().setColumn(
        1, 10
    ),
    aspirate_shift=[0, 0, asp_z_shift],
)
soloSoft.dispense(
    position="Position8",
    dispense_volumes=Plate_96_PlateOne_1833_9600_ConicalBottomStorage().setColumn(
        2, 10
    ),
    dispense_shift=[0, 0, asp_z_shift],
)

soloSoft.shuckTip()
soloSoft.savePipeline()

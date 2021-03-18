"""
CAMPAIGN 1, STEP 2: 

ANTIBIOTIC SERIAL DILUTION INTO LB MEDIA PROTOCOL

Deck Layout:
1 -> 200 uL Tips ("TipBox-Corning 200uL")
2 -> HEATING NEST
3 -> Lb media well, antibiotic stock solution well (12 channel reservoir) -> column 1 = lb media; column 2 = antibiotic stock solution 
4 -> Growth plate (Corning 3383 or Falcon - ref 353916)
5 -> Culture plate from freezer (96 deep well round bottom)
6 -> Antibiotic serial dilution plate (Corning 3383 or Falcon - ref 353916)
7 -> 10 fold culture plate dilution (Corning 3383 or Falcon - ref 353916)
8 -> Empty
"""

import os
import sys

# Change this path to point to the location of the repository, if neccessary
sys.path.append(
    os.path.abspath(
        os.path.join(os.path.abspath(os.path.dirname(__file__)), "../../src")
    )
)
from liquidhandling import SoloSoft
from liquidhandling import Plate_96_Corning_3635_ClearUVAssay, Reservoir_12col_Agilent_201256_100_BATSgroup

# from VolumeManager import VolumeManager


# * Program Variables
blowoff_volume = 20
num_mixes = 5
# Step 2 variables
media_transfer_volume_s2 = 135
first_column_transfer_volume_s2 = 150
serial_antibiotic_transfer_volume_s2 = 15
serial_source_mixing_volume_s2 = (
    100  # mix volume in antibiotic stock solution well in 12 channel reservoir
)
serial_source_num_mixes_s2 = (
    10  # num mixes in antibiotic stock solutuion well prior to first transfer
)
serial_destination_mixing_volume_s2 = 100

soloSoft = SoloSoft(
    filename="antibiotic_serial_dilution.hso",
    plateList=[
        "TipBox.200uL.Corning-4864.orangebox",
        "Empty",
        "DeepBlock.96.VWR-75870-792.sterile",
        "Plate.96.Corning-3635.ClearUVAssay",
        "DeepBlock.96.VWR-75870-792.sterile",
        "Plate.96.Corning-3635.ClearUVAssay",
        "Plate.96.Corning-3635.ClearUVAssay",
        "Empty"
    ],
)

# * Fill colums 2-6 of generic 96 well plate with lb media - NOTE: could do this at the same time as media dispensing in step 1 to save tips
soloSoft.getTip()

for i in range(2, 7):
    # no need for volume management, drawing from 12 channel at Position 3, 1st row (lb media)
    soloSoft.aspirate(
        position="Position3",
        aspirate_volumes=Reservoir_12col_Agilent_201256_100_BATSgroup().setColumn(
            1, media_transfer_volume_s2
        ),
        aspirate_shift=[0, 0, 4],
        pre_aspirate=blowoff_volume,
    )
    soloSoft.dispense(
        position="Position6",
        dispense_volumes=Plate_96_Corning_3635_ClearUVAssay().setColumn(i, media_transfer_volume_s2),
        dispense_shift=[0, 0, 2],
        blowoff=blowoff_volume,
    )

# * Transfer undiluted antibiotic stock solution (12 channel in Position 3, 2rd row) into empty first row of serial dilution plate
soloSoft.aspirate(
    position="Position3",
    aspirate_volumes=Reservoir_12col_Agilent_201256_100_BATSgroup().setColumn(
        2, first_column_transfer_volume_s2
    ),
    pre_aspirate=blowoff_volume,
    mix_at_start=True,
    mix_cycles=serial_source_num_mixes_s2,
    mix_volume=serial_source_mixing_volume_s2,
    aspirate_shift=[0, 0, 4],
    dispense_height=4,
)
soloSoft.dispense(
    position="Position6",
    dispense_volumes=Plate_96_Corning_3635_ClearUVAssay().setColumn(1, first_column_transfer_volume_s2),
    dispense_shift=[0, 0, 2],
    blowoff=blowoff_volume,
    mix_at_finish=True,
    mix_cycles=num_mixes,
    mix_volume=serial_destination_mixing_volume_s2,
    aspirate_height=2,
)

# * Serial dilution within Generic 96 well plate (Corning or Falcon) - mix 5 times before and after transfer
for i in range(1, 6):
    soloSoft.aspirate(
        position="Position6",
        aspirate_volumes=Plate_96_Corning_3635_ClearUVAssay().setColumn(
            i, serial_antibiotic_transfer_volume_s2
        ),
        aspirate_shift=[0, 0, 2],
        pre_aspirate=blowoff_volume,
        mix_at_start=True,
        mix_cycles=num_mixes,
        mix_volume=serial_destination_mixing_volume_s2,
        dispense_height=2,
    )
    soloSoft.dispense(
        position="Position6",
        dispense_volumes=Plate_96_Corning_3635_ClearUVAssay().setColumn(
            i + 1, serial_antibiotic_transfer_volume_s2
        ),
        dispense_shift=[0, 0, 2],
        blowoff=blowoff_volume,
        mix_at_finish=True,
        mix_cycles=num_mixes,
        mix_volume=serial_destination_mixing_volume_s2,
        aspirate_height=2,
    )

# no need to throw away excess volume in last column.
soloSoft.shuckTip()
soloSoft.savePipeline()

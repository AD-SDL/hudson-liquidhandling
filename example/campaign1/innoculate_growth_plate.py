"""
CAMPAIGN 1, STEP 1: 

INNOCULATE GROWTH PLATE FROM THAWED CULTURE BACTERIA PLATE

Deck Layout:
1 -> Tips ("TipBox-Corning 200uL")
2 -> Growth plate (Corning 3383 or Falcon - ref 353916)
3 -> Lb media well, antibiotic stock solution well (12 channel reservoir) -> column 1 = lb media; column 2 = antibiotic stock solution 
4 -> HEATING NEST
5 -> Culture plate from freezer (96 deep well round bottom)
6 -> Antibiotic serial dilution plate (Corning 3383 or Falcon - ref 353916)
7 -> Empty
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
import SoloSoft
from Plates import GenericPlate96Well, NinetySixDeepWell, ZAgilentReservoir_1row

# from VolumeManager import VolumeManager

# * Program Variables
blowoff_volume = 20
num_mixes = 5
# Step 1 variables
media_transfer_volume_s1 = 60
culture_transfer_volume_s1 = 30
culture_plate_mix_volume_s1 = 180
growth_plate_mix_volume_s1 = 50

soloSoft = SoloSoft.SoloSoft(
    filename="innoculate_growth_plate.hso",
    plateList=[
        "TipBox-Corning 200uL",
        "Corning 3383",
        "12 Channel Reservoir",
        "Empty",
        "96 Deep Protein",
        "Corning 3383",
        "Empty",
        "Empty",
    ],
)

# * Fill 6 rows of empty 96 well plate (corning 3383 or Falcon - ref 353916) with fresh lb media (12 channel in Position 3, column 1)
soloSoft.getTip()
j = 1
for i in range(1, 7):
    soloSoft.aspirate(
        position="Position3",
        aspirate_volumes=ZAgilentReservoir_1row().setColumn(
            1, media_transfer_volume_s1
        ),
        aspirate_shift=[
            0,
            0,
            4,
        ],  # larger shift needed for 12 channel reservoir #TODO remeasure 12 channel reservoir depth
        # pre_aspirate=blowoff_volume,
    )
    soloSoft.dispense(
        position="Position2",
        dispense_volumes=GenericPlate96Well().setColumn(i, media_transfer_volume_s1),
        # blowoff=blowoff_volume,
        dispense_shift=[0, 0, 2],
    )

# * Add bacteria from thawed culture plate (column 1) to growth plate with fresh media (columns 1-6)
for i in range(1, 7):
    soloSoft.aspirate(
        position="Position5",
        aspirate_volumes=NinetySixDeepWell().setColumn(1, culture_transfer_volume_s1),
        mix_at_start=True,
        mix_cycles=num_mixes,
        mix_volume=culture_plate_mix_volume_s1,
        dispense_height=2,
        aspirate_shift=[0, 0, 2],
        pre_aspirate=blowoff_volume,
    )
    soloSoft.dispense(
        position="Position2",
        dispense_volumes=GenericPlate96Well().setColumn(i, culture_transfer_volume_s1),
        mix_at_finish=True,
        mix_cycles=num_mixes,
        mix_volume=growth_plate_mix_volume_s1,
        aspirate_height=2,
        dispense_shift=[0, 0, 2],
        blowoff=blowoff_volume,
    )

soloSoft.shuckTip()
soloSoft.savePipeline()

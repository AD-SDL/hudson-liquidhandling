"""
CAMPAIGN 1, STEP 1: 

INNOCULATE GROWTH PLATE FROM THAWED CULTURE BACTERIA PLATE

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
import SoloSoft
from Plates import GenericPlate96Well, NinetySixDeepWell, ZAgilentReservoir_1row

# from VolumeManager import VolumeManager

# * Program Variables
blowoff_volume = 20
num_mixes = 5
# Step 1 variables
culture_plate_column_num = 2
media_transfer_volume_s1 = 60
culture_transfer_volume_s1 = 30
dilution_media_volume = 198 
dilution_culture_volume = 22
culture_plate_mix_volume_s1 = 50
growth_plate_mix_volume_s1 = 40

soloSoft = SoloSoft.SoloSoft(
    filename="innoculate_growth_plate.hso",
    plateList=[
        "TipBox-Corning 200uL",
        "Empty",
        "12 Channel Reservoir",
        "Corning 3383",
        "96 Deep Protein",
        "Corning 3383",
        "Corning 3383",
        "Empty",
    ],
)

# * Fill 6 columns of empty 96 well plate (corning 3383 or Falcon - ref 353916) with fresh lb media (12 channel in Position 3, column 1)
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
    )
    soloSoft.dispense(
        position="Position4",
        dispense_volumes=GenericPlate96Well().setColumn(i, media_transfer_volume_s1),
        dispense_shift=[0, 0, 2],
    )

# * Fill first column of culture 10 fold dilution plate with fresh lb media 
soloSoft.aspirate(
    position="Position3", 
    aspirate_volumes=ZAgilentReservoir_1row().setColumn(1, dilution_media_volume), 
    aspirate_shift=[0,0,4], 
)
soloSoft.dispense(
    position="Position7", 
    dispense_volumes=GenericPlate96Well().setColumn(1, dilution_media_volume),
    dispense_shift=[0,0,2],
)

#* Add bacteria from thawed culture plate (Position 5, column defined in variable) to dilution plate (Position 7, column 1) to make culture 10 fold dilution
soloSoft.aspirate(
    position="Position5",
    aspirate_volumes=NinetySixDeepWell().setColumn(culture_plate_column_num, dilution_culture_volume),
    aspirate_shift=[0,0,2],
    mix_at_start=True, 
    mix_cycles=num_mixes,
    mix_volume=culture_plate_mix_volume_s1,
    dispense_height=2,
    pre_aspirate=blowoff_volume,
    syringe_speed=25,
)
soloSoft.dispense(
    position="Position7", 
    dispense_volumes=GenericPlate96Well().setColumn(1, dilution_culture_volume),
    dispense_shift=[0,0,2],
    mix_at_finish=True,
    mix_cycles=num_mixes,
    mix_volume=culture_plate_mix_volume_s1,
    aspirate_height=2,
    syringe_speed=25,
    blowoff=blowoff_volume,
)

# * Add bacteria from 10 fold diluted culture plate (Position 7, column 1) to growth plate with fresh media (columns 1-6)
for i in range(1, 7):
    soloSoft.aspirate(    # already mixed the cells, no need to do it before every transfer
        position="Position7",
        aspirate_volumes=GenericPlate96Well().setColumn(1, culture_transfer_volume_s1),  
        aspirate_shift=[0, 0, 2],  # prevents 50 uL tips from going too deep in 96 deep well plate
        syringe_speed=25,
    )
    soloSoft.dispense(    # do need to mix at end of transfer 
        position="Position4",
        dispense_volumes=GenericPlate96Well().setColumn(i, culture_transfer_volume_s1),
        mix_at_finish=True,
        mix_cycles=num_mixes,
        mix_volume=growth_plate_mix_volume_s1,
        aspirate_height=2,
        dispense_shift=[0, 0, 2],
        syringe_speed=25,
    )

soloSoft.shuckTip()
soloSoft.savePipeline()

"""
CAMPAIGN STEPS 1-3

! sometimes not enough application memory in SoloSoft to load this entire .hso file

Deck Layout:
1 -> 200 uL Tips ("TipBox-Corning 200uL")
2 -> HEATING NEST
3 -> Lb media well, antibiotic stock solution well (12 channel reservoir) -> column 1 = lb media; column 2 = antibiotic stock solution 
4 -> Growth plate (Corning 3383 or Falcon - ref 353916)
5 -> Culture plate from freezer (96 deep well round bottom)
6 -> Antibiotic serial dilution plate (Corning 3383 or Falcon - ref 353916)
7 -> 10 fold culture plate dilution (Corning 3383 or Falcon - ref 353916)
8 -> Empty

TODO:
- Remeasure 12 channel reservoir depth 

"""

import os
import sys
from liquidhandling import SoloSoft
from liquidhandling import GenericPlate96Well, NinetySixDeepWell, ZAgilentReservoir_1row

# * Program variables
blowoff_volume = 20
num_mixes = 5
current_media_reservoir_volume = media_reservoir_volume = 7000

# Step 1 variables
culture_plate_column_num = 2
media_transfer_volume_s1 = 60
culture_transfer_volume_s1 = 30
dilution_media_volume = 198
dilution_culture_volume = 22
culture_plate_mix_volume_s1 = 50
growth_plate_mix_volume_s1 = 40

# Step 2 variables
media_transfer_volume_s2 = 135
first_column_transfer_volume_s2 = 150
serial_antibiotic_transfer_volume_s2 = 15
serial_source_mixing_volume_s2 = 100
serial_source_num_mixes_s2 = 10
serial_destination_mixing_volume_s2 = 100

# Step 3 variables
antibiotic_transfer_volume_s3 = 90
antibiotic_mix_volume_s3 = 90
destination_mix_volume_s3 = 120


soloSoft = SoloSoft(
    filename="steps_1_2_3.hso",
    plateList=[
        "TipBox.200uL.Corning-4864.orangebox",
        "Empty",
        "12 Channel Reservoir",
        "Corning 3383",
        "96 Deep Protein",
        "Corning 3383",
        "Corning 3383",
        "Empty",
    ],
)

"""
STEP 1: INNOCULATE GROWTH PLATE FROM SOURCE BACTERIA PLATE -----------------------------------------------------------------
"""
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
        ],
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
    aspirate_shift=[0, 0, 4],
)
soloSoft.dispense(
    position="Position7",
    dispense_volumes=GenericPlate96Well().setColumn(1, dilution_media_volume),
    dispense_shift=[0, 0, 2],
)

# * Add bacteria from thawed culture plate (Position 5, column defined in variable) to dilution plate (Position 7, column 1) to make culture 10 fold dilution
soloSoft.aspirate(
    position="Position5",
    aspirate_volumes=NinetySixDeepWell().setColumn(
        culture_plate_column_num, dilution_culture_volume
    ),
    aspirate_shift=[0, 0, 2],
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
    dispense_shift=[0, 0, 2],
    mix_at_finish=True,
    mix_cycles=num_mixes,
    mix_volume=culture_plate_mix_volume_s1,
    aspirate_height=2,
    syringe_speed=25,
    blowoff=blowoff_volume,
)

# * Add bacteria from 10 fold diluted culture plate (Position 7, column 1) to growth plate with fresh media (columns 1-6)
for i in range(1, 7):
    soloSoft.aspirate(  # already mixed the cells, no need to do it before every transfer
        position="Position7",
        aspirate_volumes=GenericPlate96Well().setColumn(1, culture_transfer_volume_s1),
        aspirate_shift=[
            0,
            0,
            2,
        ],  # prevents 50 uL tips from going too deep in 96 deep well plate
        syringe_speed=25,
    )
    soloSoft.dispense(  # do need to mix at end of transfer
        position="Position4",
        dispense_volumes=GenericPlate96Well().setColumn(i, culture_transfer_volume_s1),
        mix_at_finish=True,
        mix_cycles=num_mixes,
        mix_volume=growth_plate_mix_volume_s1,
        aspirate_height=2,
        dispense_shift=[0, 0, 2],
        syringe_speed=25,
    )

"""
STEP 2: PERFORM SERIAL DILUTIONS ON ANTIBIOTIC -------------------------------------------------------------------------------
"""
# * Fill colums 2-6 of generic 96 well plate with lb media - NOTE: could do this at the same time as media dispensing in step 1 to save tips
soloSoft.getTip()

for i in range(2, 7):
    # no need for volume management, drawing from 12 channel at Position 3, 1st row (lb media)
    soloSoft.aspirate(
        position="Position3",
        aspirate_volumes=ZAgilentReservoir_1row().setColumn(
            1, media_transfer_volume_s2
        ),
        aspirate_shift=[0, 0, 4],
        pre_aspirate=blowoff_volume,
    )
    soloSoft.dispense(
        position="Position6",
        dispense_volumes=GenericPlate96Well().setColumn(i, media_transfer_volume_s2),
        dispense_shift=[0, 0, 2],
        blowoff=blowoff_volume,
    )

# * Transfer undiluted antibiotic stock solution (12 channel in Position 3, 2rd row) into empty first row of serial dilution plate
soloSoft.aspirate(
    position="Position3",
    aspirate_volumes=ZAgilentReservoir_1row().setColumn(
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
    dispense_volumes=GenericPlate96Well().setColumn(1, first_column_transfer_volume_s2),
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
        aspirate_volumes=GenericPlate96Well().setColumn(
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
        dispense_volumes=GenericPlate96Well().setColumn(
            i + 1, serial_antibiotic_transfer_volume_s2
        ),
        dispense_shift=[0, 0, 2],
        blowoff=blowoff_volume,
        mix_at_finish=True,
        mix_cycles=num_mixes,
        mix_volume=serial_destination_mixing_volume_s2,
        aspirate_height=2,
    )
# no need to throw away excess volume from last column of serial dilution


"""
STEP 3: ADD ANTIBIOTIC TO CULTURE PLATES -------------------------------------------------------------------------------------
"""
# soloSoft.getTip() # no need to get tips here unless steps separated into indivudual files
for i in range(6, 0, -1):
    soloSoft.aspirate(
        position="Position6",
        aspirate_volumes=GenericPlate96Well().setColumn(
            i, antibiotic_transfer_volume_s3
        ),
        mix_at_start=True,
        mix_cycles=num_mixes,
        mix_volume=antibiotic_mix_volume_s3,
        dispense_height=2,
        aspirate_shift=[0, 0, 2],
    )
    soloSoft.dispense(
        position="Position4",
        dispense_volumes=GenericPlate96Well().setColumn(
            i, antibiotic_transfer_volume_s3
        ),
        mix_at_finish=True,
        mix_cycles=num_mixes,
        mix_volume=destination_mix_volume_s3,
        aspirate_height=2,
        dispense_shift=[0, 0, 2],
    )

soloSoft.shuckTip()
soloSoft.savePipeline()

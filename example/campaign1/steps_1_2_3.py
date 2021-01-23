"""
CAMPAIGN STEPS 1-3

Deck Layout:
1 -> Tips
2 -> Destination culture plate (starts empty) - Corning 3383
3 -> media well (lb)
4 -> HEATING NEST
5 -> bacterial plate from freezer (what plate type is this? corning 3383 for now)
6 -> (serial dilution of antibiotic end plate, not needed for this run alone)
7 -> Empty
8 -> Antibiotic well (from stock solution) (what plate type will this be? 96 deep well for now)
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
from Plates import (
    GenericPlate96Well,
    NinetySixDeepWell,
    ZAgilentReservoir_1row,
)  # TODO: determine which plate types you will actually need

# * Program variables
blowoff_volume = 20
num_mixes = 10
current_media_reservoir_volume = (
    media_reservoir_volume
) = 7000  # use to check that you have media left in the well to aspirate

# Step 1 variables
# can be a 5 num mixes
media_transfer_volume_s1 = 60
culture_transfer_volume_s1 = 30
culture_plate_mix_volume_s1 = 180
growth_plate_mix_volume_s1 = 60

# Step 2 variables
media_transfer_volume_s2 = 180
serial_antibiotic_transfer_volume_s2 = 20
serial_source_mixing_volume_s2 = 100
serial_destination_mixing_volume_s2 = (
    150  # must be less than total volume, otherwise it draws up air
)


# Step 3 variables
antibiotic_transfer_volume_s3 = 90
antibiotic_mix_volume_s3 = 100
destination_mix_volume_s3 = 150


soloSoft = SoloSoft.SoloSoft(
    filename="steps_1_2_3.hso",
    plateList=[
        "TipBox-Corning 200uL",
        "Corning 3383",
        "12 Channel Reservoir",
        "Empty",
        "Corning 3383",
        "Corning 3383",
        "Empty",
        "96 Deep Protein",
    ],
)

"""
STEP 1: INNOCULATE GROWTH PLATE FROM SOURCE BACTERIA PLATE -----------------------------------------------------------------
"""

# * Idea: fill empty 96 well plate (corning 3383) with fresh media (lb) (fill the whole plate?)
soloSoft.getTip()
j = 1
for i in range(1, 13):
    # volume management (not necessary if media is in a trough -> only needed for this 12 channel reservoir)
    current_media_reservoir_volume = (
        current_media_reservoir_volume - 8 * media_transfer_volume_s1
    )
    if current_media_reservoir_volume < 8 * media_transfer_volume_s1:
        j += 1
        current_media_reservoir_volume = media_reservoir_volume
    soloSoft.aspirate(
        position="Position3",
        aspirate_volumes=ZAgilentReservoir_1row().setColumn(
            j, media_transfer_volume_s1
        ),
        aspirate_shift=[
            0,
            0,
            4,
        ],  # larger shift needed for 12 channel reservoir #TODO remeasure 12 channel reservoir depth
        pre_aspirate=blowoff_volume,
    )
    soloSoft.dispense(
        position="Position2",
        dispense_volumes=GenericPlate96Well().setColumn(i, media_transfer_volume_s1),
        blowoff=blowoff_volume,
        dispense_shift=[0, 0, 2],
    )

# * add culture from thawed culture plate (column 1) to newly created growth plate with fresh media (columns 1-6)
# no need to get tips
for i in range(1, 7):
    soloSoft.aspirate(
        position="Position5",
        aspirate_volumes=NinetySixDeepWell().setColumn(
            1, culture_transfer_volume_s1
        ),  # TODO change plate type to 96 deep well round bottom
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

"""
STEP 2: PERFORM SERIAL DILUTIONS ON ANTIBIOTIC -------------------------------------------------------------------------------
"""

soloSoft.getTip()

# * Fill half plate (6 columns) of generic 96 well plate with lb media (could do this at the same time as media distribition in step 1)
# use the variable j already defined (should choose the approprate well of 12 channel reservoir)
for i in range(1, 7):
    # volume management
    current_media_reservoir_volume = (
        current_media_reservoir_volume - 8 * media_transfer_volume_s2
    )
    if current_media_reservoir_volume < 8 * media_transfer_volume_s2:
        j += 1
        current_media_reservoir_volume = media_reservoir_volume
    soloSoft.aspirate(
        position="Position3",
        aspirate_volumes=ZAgilentReservoir_1row().setColumn(
            j, media_transfer_volume_s2
        ),
        aspirate_shift=[
            0,
            0,
            4,
        ],  # larger shift needed for 12 channel reservoir # TODO fix this/remeasure 12 channel
        pre_aspirate=blowoff_volume,
    )
    soloSoft.dispense(
        position="Position6",
        dispense_volumes=GenericPlate96Well().setColumn(i, media_transfer_volume_s2),
        dispense_shift=[0, 0, 2],
        blowoff=blowoff_volume,
    )

# * Make first 10 fold dilution (from antibiotic reservoir to first row of destination plate)
# no need to get tips here
soloSoft.aspirate(
    position="Position8",
    aspirate_volumes=NinetySixDeepWell().setColumn(
        1, serial_antibiotic_transfer_volume_s2
    ),
    pre_aspirate=blowoff_volume,
    mix_at_start=True,
    mix_cycles=num_mixes,
    mix_volume=serial_source_mixing_volume_s2,
    aspirate_shift=[0, 0, 2],
    dispense_height=2,
)
soloSoft.dispense(
    position="Position6",
    dispense_volumes=GenericPlate96Well().setColumn(
        1, serial_antibiotic_transfer_volume_s2
    ),
    dispense_shift=[0, 0, 2],
    blowoff=blowoff_volume,
    mix_at_finish=True,
    mix_cycles=num_mixes,
    mix_volume=serial_destination_mixing_volume_s2,
    aspirate_height=2,
)

# * serial dilution within Generic 96 well plate (Corning 3383?)
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

# no need to throw away excess volume in last column. only need to transfer a set volume into cell growth plate


"""
STEP 3: ADD ANTIBIOTIC TO CULTURE PLATES -------------------------------------------------------------------------------------
"""

# no need to get tips (just ended at smallest serial dilution) -> work backwards in growth plate
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
        pre_aspirate=blowoff_volume,
    )
    soloSoft.dispense(
        position="Position2",
        dispense_volumes=GenericPlate96Well().setColumn(
            i, antibiotic_transfer_volume_s3
        ),
        mix_at_finish=True,
        mix_cycles=num_mixes,
        mix_volume=destination_mix_volume_s3,
        aspirate_height=2,
        dispense_shift=[0, 0, 2],
        blowoff=blowoff_volume,
    )

soloSoft.shuckTip()
soloSoft.savePipeline()

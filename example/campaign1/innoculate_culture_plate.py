"""
CAMPAIGN 1, STEP 1: 

INNOCULATE CULTURE PLATES FROM SOURCE BACTERIA PLATE 

Deck Layout:
1 -> Tips
2 -> Destination culture plate (starts empty) - Corning 3383
3 -> media well (lb)
4 -> HEATING NEST
5 -> bacterial plate from freezer (what plate type is this? corning 3383 for now)
6 -> (serial dilution of antibiotic end plate, not needed for this run alone)
7 -> Empty
8 -> Antibiotic well (from stock solution) (what plate type will this be? 96 deep well for now)

IDEA (FOR NOW):
- end up with 100 ul cells and new agar (then can add 100ul of new agar with antibiotics) -> 200ul total at the end of first 3 campaign steps


QUESTIONS:
- is mixing too many times harmful to the cells?
- what volumes should be transfered?
"""

import os
import sys

# Change this path to point to the location of the repository, if neccessary
sys.path.append(
    os.path.abspath(os.path.join(os.path.abspath(os.path.dirname(__file__)), "../../src"))
)
import SoloSoft
from Plates import GenericPlate96Well, NinetySixDeepWell, ZAgilentReservoir_1row    # TODO: determine which plate types you will actually need

#* Program variables
media_transfer_volume = 60
culture_transfer_volume = 40
current_media_reservoir_volume = media_reservoir_volume = 7000 # use to check that you have media left in the well to aspirate
culture_well_volume = 100 # might not need this 
blowoff_volume = 20
num_mixes = 10 # might not need to mix
culture_plate_mix_volume = 70
growth_plate_mix_volume = 70

# define the deck layout
soloSoft = SoloSoft.SoloSoft(
    filename="innoculate_culture_plate.hso",
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

#* fill empty 96 well plate (corning 3383) with fresh media (lb) (fill the whole plate?) 
soloSoft.getTip()
j = 1
for i in range(1,13):
    # volume management (not necessary if media is in a trough -> only needed for this 12 channel reservoir)
    current_media_reservoir_volume = current_media_reservoir_volume - 8 * media_transfer_volume
    if current_media_reservoir_volume < 8 * media_transfer_volume:
        j += 1
        current_media_reservoir_volume = media_reservoir_volume
    soloSoft.aspirate(
        position="Position3",
        aspirate_volumes=ZAgilentReservoir_1row().setColumn(j, media_transfer_volume),
        aspirate_shift=[0,0,4], # larger shift needed for 12 channel reservoir #TODO remeasure 12 channel reservoir depth
        pre_aspirate=blowoff_volume,
    )
    soloSoft.dispense(
        position="Position2", 
        dispense_volumes=GenericPlate96Well().setColumn(i, media_transfer_volume), 
        blowoff=blowoff_volume, 
        dispense_shift=[0,0,2],
    )

#* Transfer from column 1 of culture plate (thawed) to columns 1-6 of growth plate
# might be able to make this more efficient (aspirate large enough volume to dipense all at once?)
soloSoft.getTip() # is this needed here? 
for i in range(1,7):
    soloSoft.aspirate(
        position="Position5", 
        aspirate_volumes=GenericPlate96Well().setColumn(1, culture_transfer_volume), 
        mix_at_start=True, 
        mix_cycles=num_mixes, 
        mix_volume=culture_plate_mix_volume, 
        dispense_height=2,
        aspirate_shift=[0,0,2], 
        pre_aspirate=blowoff_volume,
    )
    soloSoft.dispense(
        position="Position2", 
        dispense_volumes=GenericPlate96Well().setColumn(i, culture_transfer_volume), 
        mix_at_finish=True, 
        mix_cycles=num_mixes, 
        mix_volume=growth_plate_mix_volume, 
        aspirate_height=2, 
        dispense_shift=[0,0,2],
        blowoff=blowoff_volume,
    )

soloSoft.shuckTip()

soloSoft.savePipeline() 












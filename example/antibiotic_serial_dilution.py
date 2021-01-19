"""
ANTIBIOTIC SERIAL DILUTION INTO LB MEDIA PROTOCOL

6X, 10 fold dilition. Half of 96 well plate used (8 replicates)

"""

import os
import sys

# Change this path to point to the location of the repository, if neccessary
sys.path.append(
    os.path.abspath(os.path.join(os.path.abspath(os.path.dirname(__file__)), "../src"))
)
import SoloSoft
from Plates import GenericPlate96Well, NinetySixDeepWell, ZAgilentReservoir_1row
#from VolumeManager import VolumeManager


# * Program Constants
current_media_reservoir_volume = media_reservoir_volume = 7000 # TODO decide what reservoir will hold lb media (12 channel reservoir assumption right now)
media_reservoir_aspirate_volume = 180
antibiotic_source_mixing_volume = 100  
destination_mixing_volume = 150  # must be less than total volume, otherwise it draws up air
antibiotic_transfer_volume = 20
num_mixes = 5
blowoff_volume = 20

soloSoft = SoloSoft.SoloSoft(
    filename="antibiotic_serial_dilution.hso",
    plateList=[
        "TipBox-Corning 200uL",
        "Corning 3383",
        "12 Channel Reservoir",
        "Empty",
        "Empty",
        "96 Deep Protein",
        "Empty",
        "Empty",
    ],
)
# volumeManager = VolumeManager(ZAgilentReservoir_1row(), 7, 1, 1) #TODO Update placeholder values - https://www.agilent.com/store/en_US/LCat-SubCat1ECS_112089/Reservoirs


soloSoft.getTip() # default position 1 ok

#* Fill half plate (6 columns) of generic 96 well plate with lb media
j=1
for i in range(1,7):
    # volume management
    current_media_reservoir_volume = current_media_reservoir_volume - 8 * media_reservoir_aspirate_volume
    if current_media_reservoir_volume < 8 * media_reservoir_aspirate_volume:
        j += 1
        current_media_reservoir_volume = media_reservoir_volume
    soloSoft.aspirate(
        position="Position3",
        aspirate_volumes=ZAgilentReservoir_1row().setColumn(j, media_reservoir_aspirate_volume),
        aspirate_shift=[0,0,4], # larger shift needed for 12 channel reservoir # TODO fix this/remeasure 12 channel
        pre_aspirate=blowoff_volume,
    )
    soloSoft.dispense(
        position="Position2",
        dispense_volumes=GenericPlate96Well().setColumn(i, media_reservoir_aspirate_volume),
        dispense_shift=[0,0,2],
        blowoff=blowoff_volume,
    )

#* Make first 10 fold dilution (from antibiotic reservoir to first row of destination plate)
soloSoft.getTip()
soloSoft.aspirate(
    position="Position6",
    aspirate_volumes=NinetySixDeepWell().setColumn(1, antibiotic_transfer_volume), 
    pre_aspirate=blowoff_volume,
    mix_at_start=True,
    mix_cycles=num_mixes,
    mix_volume=antibiotic_source_mixing_volume,
    aspirate_shift=[0,0,2],
    dispense_height=2,
)
soloSoft.dispense(
    position="Position2", 
    dispense_volumes=GenericPlate96Well().setColumn(1, antibiotic_transfer_volume), 
    dispense_shift=[0,0,2],
    blowoff=blowoff_volume,
    mix_at_finish=True,
    mix_cycles=num_mixes,
    mix_volume=destination_mixing_volume,
    aspirate_height=2,
)

#* serial dilution within Generic 96 deep well plate

for i in range(1,6):
    soloSoft.getTip()
    soloSoft.aspirate(
        position="Position2", 
        aspirate_volumes=GenericPlate96Well().setColumn(i, antibiotic_transfer_volume), 
        aspirate_shift=[0,0,2], 
        pre_aspirate=blowoff_volume,
        mix_at_start=True, 
        mix_cycles=num_mixes,
        mix_volume=destination_mixing_volume, 
        dispense_height=2, 
    )
    soloSoft.dispense(
        position="Position2",
        dispense_volumes=GenericPlate96Well().setColumn(i+1, antibiotic_transfer_volume), 
        dispense_shift=[0,0,2],
        blowoff=blowoff_volume, 
        mix_at_finish=True, 
        mix_cycles=num_mixes,
        mix_volume=destination_mixing_volume, 
        aspirate_height=2,
)

#* Throw away the extra volume from the final dilution (no need to get new tips)
soloSoft.aspirate(  # already mixed, don't need to do again. 
    position="Position2", 
    aspirate_volumes=GenericPlate96Well().setColumn(6, antibiotic_transfer_volume), 
    aspirate_shift=[0,0,2], 
    pre_aspirate=blowoff_volume, 
    )
soloSoft.shuckTip()  # TODO: decide where this excess should be disposed of

soloSoft.savePipeline()


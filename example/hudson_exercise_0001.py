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
current_reservoir_volume = reservoir_volume = 7000
reservoir_aspirate_volume = 180
source_mixing_volume = 100
destination_mixing_volume = 200
source_volume = 20
source_num_mixes = 5
destination_num_mixes = 5


soloSoft = SoloSoft.SoloSoft(
    filename="hudson_exercise_0001.hso",
    plateList=[
        "TipBox-Corning 200uL",
        "Empty",
        "Empty",
        "Empty",
        "Empty",
        "12 Channel Reservoir",
        "96 Deep Protein",
        "Corning 3383",
    ],
)
# volumeManager = VolumeManager(ZAgilentReservoir_1row(), 7, 1, 1) #TODO Update placeholder values - https://www.agilent.com/store/en_US/LCat-SubCat1ECS_112089/Reservoirs


soloSoft.getTip()

# * Fill each row of Plate 8 w/ "aspirate_volume" worth of water from reservoir
# TODO Build into api: w/ starting point in the reservoir and range in destination plate
j = 1
for i in range(1, 13):
    current_reservoir_volume = current_reservoir_volume - 8 * reservoir_aspirate_volume
    if current_reservoir_volume < 8 * reservoir_aspirate_volume:
        j += 1
        current_reservoir_volume = reservoir_volume
    soloSoft.aspirate(
        position="Position6",
        aspirate_volumes=ZAgilentReservoir_1row().setColumn(j, reservoir_aspirate_volume),
        aspirate_shift=[0, 0, 2],
    )
    soloSoft.dispense(
        position="Position8",
        dispense_volumes=GenericPlate96Well().setColumn(i, reservoir_aspirate_volume),
        dispense_shift=[0, 0, 2],
    )

# * Mixing step
for i in range(1, 13):
    soloSoft.getTip()
    soloSoft.aspirate(
        position="Position7",
        mix_cycles=source_num_mixes,
        mix_at_start=True,
        mix_volume=source_mixing_volume,
        aspirate_volumes=NinetySixDeepWell().setColumn(i, source_volume),
        aspirate_shift=[0, 0, 2],
    )
    soloSoft.dispense(
        position="Position8",
        mix_cycles=destination_num_mixes,
        mix_at_finish=True,
        mix_volume=destination_mixing_volume,
        dispense_volumes=GenericPlate96Well().setColumn(i, source_volume),
        dispense_shift=[0, 0, 2],
    )

soloSoft.savePipeline()
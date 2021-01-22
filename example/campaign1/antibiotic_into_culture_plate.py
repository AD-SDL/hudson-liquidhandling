"""
CAMPAIGN 1. STEP 3: ADD ANTIBIOTIC TO CULTURE PLATES

Idea: 
-Transfer set volume from Column1 of antibiotic dilution plate to Column 1 of inoculated growth media plate
-Transfer set volume from Colum 2 of antibiotic dilution plate to Column 2 of inoculated growth media plate
. . . ect. 

"""

import os
import sys

# Change this path to point to the location of the repository, if neccessary
sys.path.append(
    os.path.abspath(os.path.join(os.path.abspath(os.path.dirname(__file__)), "../../src"))
)
import SoloSoft
from Plates import GenericPlate96Well, NinetySixDeepWell, ZAgilentReservoir_1row   # TODO: determine which plate types you will actually need

#* Program Variables
antibiotic_transfer_volume = 75
blowoff_volume = 20
num_mixes = 10  # will mixing too much be too stressfull on cells? we are plannign to shake when incubating anyway
antibiotic_mix_volume = 100 
destination_mix_volume = 150


soloSoft = SoloSoft.SoloSoft(
    filename="antibiotic_serial_dilution.hso",
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

#* transfer antibiotics into bacteria plate
    # if you just finished the last antibiotic dilution, could use the same tips and work backwards? 
        # for i in range(6,0,-1): <- this is the for loop to go backwards

for i in range(1,7):
    soloSoft.getTip() # take this out when you combine all three steps. 
    soloSoft.aspirate(
        position="Position6", 
        aspirate_volumes=GenericPlate96Well().setColumn(i, antibiotic_transfer_volume), 
        mix_at_start=True, 
        mix_cycles=num_mixes, 
        mix_volume=antibiotic_mix_volume,
        dispense_height=2, 
        aspirate_shift=[0,0,2], 
        pre_aspirate=blowoff_volume,
    )
    soloSoft.dispense(
        position="Position2", 
        dispense_volumes=GenericPlate96Well().setColumn(i, antibiotic_transfer_volume),
        mix_at_finish=True,
        mix_cycles=num_mixes,
        mix_volume=destination_mix_volume, 
        aspirate_height=2, 
        dispense_shift=[0,0,2], 
        blowoff=blowoff_volume,
    )

soloSoft.shuckTip()
soloSoft.savePipeline() 











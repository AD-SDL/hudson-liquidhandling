import sys
import os

# Change this path to point to the location of the repository, if neccessary
sys.path.append(
    os.path.abspath(
        os.path.join(os.path.abspath(os.path.dirname(__file__)), "../../src")
    )
)
import SoloSoft
from Plates import GenericPlate96Well

# Initialize Pipeline
soloSoft = SoloSoft.SoloSoft(
    filename="stress_test.hso",
    plateList=[
        "TipBox-200uL Corning 4864",
        "TipBox-50uL EV-50-R-S",
        "TipBox-50uL EV-50-R-S",
        "Empty",
        "Empty",
        "Agilent 12 Channel Reservoir (#201256-100) ",
        "Omni",
        "Falcon 353916- round 96",
    ],
)

# Main sequence of steps that we need to repeat across multiple rows
def sub_pipeline(i, interim_get_tips=False, interim_pause=False):
    soloSoft.getTip(position="Position2")
    soloSoft.aspirate(
        position="Position8",
        aspirate_shift=[0, 0, 0.2],
        syringe_speed=50,
        mix_at_start=True,
        mix_cycles=5,
        mix_volume=30,
        dispense_height=2,
        post_aspirate=1,
        aspirate_volumes=GenericPlate96Well().setColumn(i, 10),
    )
    soloSoft.dispense(
        position="Position8",
        dispense_shift=[0, 0, 0.2],
        syringe_speed=50,
        mix_at_finish=True,
        mix_cycles=5,
        mix_volume=50,
        aspirate_height=0.5,
        dispense_volumes=GenericPlate96Well().setColumn(i + 1, 10),
    )
    if interim_pause:
        soloSoft.pause(allow_end_run=True, pause_message="finished first half")
    if interim_get_tips:
        soloSoft.getTip(position="Position2")
    soloSoft.aspirate(
        position="Position8",
        aspirate_shift=[0, 0, 0.5],
        syringe_speed=100,
        aspirate_volumes=GenericPlate96Well().setColumn(i, 3.5),
    )
    soloSoft.dispense(
        position="Position7",
        dispense_shift=[0, 0, 0.5],
        syringe_speed=100,
        dispense_volumes=GenericPlate96Well().setColumn(i, 3.5),
    )


# Generate Pipeline
for i in range(1, 12):
    if i == 1:
        sub_pipeline(i, True)
    elif i == 6:
        sub_pipeline(i, True, True)
    else:
        sub_pipeline(i)
soloSoft.getTip(position="Position2")
soloSoft.aspirate(
    position="Position8",
    aspirate_shift=[0, 0, 0.5],
    syringe_speed=100,
    aspirate_volumes=GenericPlate96Well().setColumn(12, 3.5),
)
soloSoft.dispense(
    position="Position7",
    dispense_shift=[0, 0, 0.5],
    syringe_speed=100,
    dispense_volumes=GenericPlate96Well().setColumn(12, 3.5),
)
soloSoft.shuckTip()
soloSoft.savePipeline()

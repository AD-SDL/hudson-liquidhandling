import sys

# Change this path to point to the location of the repository, if neccessary
sys.path.append("E:\\Dev\\repos\\liquidhandling\\src")
import SoloSoft
from Plates import Plate96Well

soloSoft = SoloSoft.SoloSoft(
    filename="agilent_rese.hso",
    plateList=[
        "TipBox-Corning 200uL",
        "Corning 3383",
        "Corning 3383",
        "Corning 3383",
        "Corning 3383",
        "Z_Agilent_Reservoir_1row",
        "Corning 3383",
        "Corning 3635",
    ],
)

soloSoft.startLoop(6)
soloSoft.getTips()
# Add 6 aspirate/dispense cycles
for i in range(1, 7):
    soloSoft.aspirate(
        position="Position6",
        aspirate_shift=[0, 0, 2],
        aspirate_volumes=Plate96Well().setColumn(6, 180),
    )
    soloSoft.dispense(
        position="Position8",
        dispense_shift=[0, 0, 2],
        dispense_volumes=Plate96Well().setColumn(i, 180),
    )
soloSoft.shuckTips()
soloSoft.getTips()
# Add 6 aspirate/dispense cycles
for i in range(1, 7):
    soloSoft.aspirate(
        position="Position6",
        aspirate_shift=[0, 0, 2],
        aspirate_volumes=Plate96Well().setColumn(8, 180),
    )
    soloSoft.dispense(
        position="Position8",
        dispense_shift=[0, 0, 2],
        dispense_volumes=Plate96Well().setColumn(i + 6, 180),
    )
soloSoft.shuckTips()
soloSoft.pause(
    pause_message="Finished plate. Reload buffers and destination plate. Please give me a break, humans!",
    allow_end_run=True,
)
soloSoft.endLoop()
soloSoft.moveArm()

soloSoft.savePipeline()
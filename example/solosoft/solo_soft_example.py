import sys
import os

# Change this path to point to the location of the repository, if neccessary
sys.path.append(
    os.path.abspath(
        os.path.join(os.path.abspath(os.path.dirname(__file__)), "../../src")
    )
)
import SoloSoft

soloSoft = SoloSoft.SoloSoft(
    filename="example.hso",
    plateList=[
        "TipBox-Corning 200uL",
        "Corning 3383",
        "Corning 3383",
        "Corning 3383",
        "Corning 3383",
        "Corning 3383",
        "Corning 3383",
        "Corning 3383",
    ],
)

soloSoft.getTip()
soloSoft.loop(1)
soloSoft.aspirate()
soloSoft.dispense()
soloSoft.endLoop()
soloSoft.moveArm()

print(soloSoft.pipeline)

soloSoft.savePipeline()

import sys

# Change this path to point to the location of the repository, if neccessary
sys.path.append("E:\\Dev\\repos\\liquidhandling\\src")
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

soloSoft.getTips()
soloSoft.startLoop(1)
soloSoft.aspirate()
soloSoft.dispense()
soloSoft.endLoop()
soloSoft.moveArm()

soloSoft.savePipeline()
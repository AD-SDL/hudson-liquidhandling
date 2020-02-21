import sys

sys.path.append("C:\\Users\\ryand\\Dev\\repos\\liquidhandling\\src")
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
import sys
import os
from liquidhandling import SoloSoft

soloSoft = SoloSoft(
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

# print(soloSoft.pipeline)

soloSoft.savePipeline(CRLF=True)

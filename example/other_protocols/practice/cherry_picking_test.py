from liquidhandling import SoftLinx, SoloSoft
from liquidhandling import *

soloSoft = SoloSoft(
    filename="cherry_picking_test.hso", 
    plateList=[
        "TipBox.50uL.Axygen-EV-50-R-S.tealbox",
        "Empty",
        "Empty",
        "Empty",
        "Empty",
        "Empty",
        "Empty",
        "Plate.96.Corning-3635.ClearUVAssay",  
    ]
)

soloSoft.getTip()
soloSoft.aspirate(
    position="Position8", 
    aspirate_volumes=Plate_96_Corning_3635_ClearUVAssay().setColumn(1,50),
    aspirate_shift = [0,0,2],
)

for i in range(3):
    soloSoft.dispense(
        position="Position8", 
        dispense_volumes=Plate_96_Corning_3635_ClearUVAssay().setColumn(2,10), 
        dispense_shift =[0,0,2], 
    )

soloSoft.shuckTip()
soloSoft.savePipeline()

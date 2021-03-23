from liquidhandling import SoftLinx, SoloSoft
from liquidhandling import *

#* Program Variables 
trans_volume = 10
default_z_shift = .5

#* Initialize Solo
soloSoft = SoloSoft(
    filename="plate_test_384.hso", 
    plateList=[
        "Empty",
        "Empty",
        "Empty",
        "Empty",
        "Empty",
        "Empty",
        "TipBox.50uL.Axygen-EV-50-R-S.tealbox",
        "Plate.384.Corning-3540.BlackwClearBottomAssay",  
    ]
)

soloSoft.getTip("Position7")
soloSoft.aspirate(
    position="Position8", 
    aspirate_volumes=Plate_384_Corning_3540_BlackwClearBottomAssay().setColumn(1,trans_volume),
    aspirate_shift = [0,0,default_z_shift],
)
soloSoft.dispense(
    position="Position8", 
    dispense_volumes=Plate_384_Corning_3540_BlackwClearBottomAssay().setColumn(2,trans_volume), 
    dispense_shift =[0,0,default_z_shift], 
)
soloSoft.shuckTip()
soloSoft.savePipeline()


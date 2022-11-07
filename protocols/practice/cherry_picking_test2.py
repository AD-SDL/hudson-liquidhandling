from liquidhandling import SoftLinx, SoloSoft
from liquidhandling.CherryPicking import CherryPicking
from liquidhandling.Plates import Plate_96_Corning_3635_ClearUVAssay

origins = ["A1", "A2", "A3"]
destinations = ["B1", "B2", "B3"]
volume = 10
default_z_shift = 2

soloSoft = SoloSoft(
    filename="C:\\Users\\svcaibio\\Desktop\\Debug\\cherry_picking_test_2.hso",
    plateList=[
        "Empty",
        "Empty",
        "TipBox.50uL.Axygen-EV-50-R-S.tealbox",
        "Empty",
        "Empty",
        "Empty",
        "Empty",
        "Plate.96.Corning-3635.ClearUVAssay",
    ],
)

for i in range(len(origins)): 
    soloSoft.getTip("Position3", num_tips=1)
    soloSoft.aspirate(
        position="Position8",
        aspirate_volumes=Plate_96_Corning_3635_ClearUVAssay().setCell(origins[i][0], int(origins[i][1:]), volume), 
        aspirate_shift=[0, 0, default_z_shift],
    )
    soloSoft.dispense(
        position="Position8",
        dispense_volumes=Plate_96_Corning_3635_ClearUVAssay().setCell(destinations[i][0], int(destinations[i][1:]), volume), 
        dispense_shift=[0,0,default_z_shift],
    )
    
soloSoft.shuckTip()

soloSoft.savePipeline()
#import necessary packages
from liquidhandling import SoftLinx, SoloSoft
from liquidhandling import *

#define common variables
mixCycles = 0
dispenseHeight = 2
aspirateHeight = 2
syringeSpeed = 50
# #define variables aspirating Competent Cells
# mixVolumeAspirateCompetent = 25
# #define variables dispensing Competent Cells
# mixVolumeDispenseCompetent = 25
# #define variables aspirating DNA ligation
# mixVolumeAspirateDNALigation = 10
# #define variables dispensing DNA ligation
# mixVolumeDispenseDNALigation = 15

Path = "C:\\Users\\svcaibio\\Dev\\liquidhandling\\PyHamilton\\practice\\"

#liquidhandling chunk using SoloSoft
# defining the plates on solosoft
soloSoft = SoloSoft(
    filename = "testproto.hso",
    plateList = [
        "Empty",
        "Empty",
        "TipBox.50uL.Axygen-EV-50-R-S.tealbox",
        "Plate.96.Corning-3635.ClearUVAssay", #Working plate -empty at start
        "Empty",#Competent cells assuming is full plate
        "Empty",
        "Empty",
        "Plate.96.Corning-3635.ClearUVAssay",
    ],
)
#Aspirate competent cells
for i in range(1,4):
    soloSoft.getTip("Position3")
    soloSoft.aspirate(
        position = "Position4",
        aspirate_volumes = Plate_96_Corning_3635_ClearUVAssay().setColumn(i, 25),
        aspirate_shift = [0, 0, 2],
#         mix_at_start = True,
#         mix_cycles = mixCycles,
#         mix_volume = mixVolumeAspirateCompetent,
        dispense_height = dispenseHeight,
        syringe_speed = syringeSpeed,
    )

    soloSoft.dispense(
        position = "Position8",
        dispense_volumes = Plate_96_Corning_3635_ClearUVAssay().setColumn(i, 25),
        dispense_shift = [0, 0, 2],
#         mix_at_finish = True,
#         mix_cycles = mixCycles,
#         mix_volume = mixVolumeDispenseCompetent,
        aspirate_height = aspirateHeight,
        syringe_speed = syringeSpeed,
    )
soloSoft.shuckTip() 

#Aspirate competent cells
for i in range(1,4):
    soloSoft.getTip("Position3")
    soloSoft.aspirate(
        position = "Position8",
        aspirate_volumes = Plate_96_Corning_3635_ClearUVAssay().setColumn(i, 25),
        aspirate_shift = [0, 0, 2],
#         mix_at_start = True,
#         mix_cycles = mixCycles,
#         mix_volume = mixVolumeAspirateCompetent,
        dispense_height = dispenseHeight,
        syringe_speed = syringeSpeed,
    )

    soloSoft.dispense(
        position = "Position4",
        dispense_volumes = Plate_96_Corning_3635_ClearUVAssay().setColumn(i, 25),
        dispense_shift = [0, 0, 2],
#         mix_at_finish = True,
#         mix_cycles = mixCycles,
#         mix_volume = mixVolumeDispenseCompetent,
        aspirate_height = aspirateHeight,
        syringe_speed = syringeSpeed,
    )
soloSoft.shuckTip() 
soloSoft.savePipeline() 

####################################################################################################

softLinx = SoftLinx("Testprotocol", "C:\\Users\\svcaibio\\Dev\\liquidhandling\\PyHamilton\\practice\\Testprotocol.slvp") # display name, path to saves

softLinx.setPlates({"SoftLinx.Solo.Position4":"Plate_96_Corning_3635_ClearUVAssay"})
softLinx.soloSoftRun("C:\\Users\\svcaibio\\Dev\\liquidhandling\\PyHamilton\\practice\\testproto.hso")
softLinx.plateCraneMoveCrane("SoftLine.PlateCrane.Safe")
softLinx.plateCraneMovePlate(["SoftLinx.Solo.Position4"],["SoftLinx.PlateCrane.Stack1"],poolID = 1)
softLinx.plateCraneMoveCrane("SoftLine.PlateCrane.Safe") #mention poolID=stack from where you get it
softLinx.saveProtocol()

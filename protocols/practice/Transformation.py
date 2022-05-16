#import necessary packages
from liquidhandling import SoftLinx, SoloSoft
from liquidhandling import *

#define common variables
mixCycles = 3
dispenseHeight = 2
aspirateHeight = 2
syringeSpeed = 50
#define variables aspirating Competent Cells
mixVolumeAspirateCompetent = 25
#define variables dispensing Competent Cells
mixVolumeDispenseCompetent = 25
#define variables aspirating DNA ligation
mixVolumeAspirateDNALigation = 10
#define variables dispensing DNA ligation
mixVolumeDispenseDNALigation = 15

Path = "/Users/priyankavsetty/hudson-liquidhandling/scripts/"

#liquidhandling chunk using SoloSoft
# defining the plates on solosoft
soloSoft = SoloSoft(
    filename = "CompetentCells.hso",
    plateList = [
        "Empty",
        "Empty",
        "TipBox.50uL.Axygen-EV-50-R-S.tealbox",
        "Plate.96.Corning-3635.ClearUVAssay", #Working plate -empty at start
        "Plate.96.Corning-3635.ClearUVAssay",#Competent cells assuming is full plate
        "Plate.96.Corning-3635.ClearUVAssay",#DNA ligation assuming is full plate
        "Empty",
        "Empty",
    ],
)
#Aspirate competent cells
for i in range(1,13):
    soloSoft.getTip("Position3")
    soloSoft.aspirate(
        position = "Position5",
        aspirate_volumes = Plate_96_Corning_3635_ClearUVAssay().setColumn(i, 25),
        aspirate_shift = [0, 0, 2],
        mix_at_start = True,
        mix_cycles = mixCycles,
        mix_volume = mixVolumeAspirateCompetent,
        dispense_height = dispenseHeight,
        syringe_speed = syringeSpeed,
    )

    soloSoft.dispense(
        position = "Position4",
        dispense_volumes = Plate_96_Corning_3635_ClearUVAssay().setColumn(i, 25),
        dispense_shift = [0, 0, 2],
        mix_at_finish = True,
        mix_cycles = mixCycles,
        mix_volume = mixVolumeDispenseCompetent,
        aspirate_height = aspirateHeight,
        syringe_speed = syringeSpeed,
    )
soloSoft.shuckTip()
soloSoft.savePipeline()
# -------------------------------------------------------------------------------
# defining the plates on solosoft
soloSoft = SoloSoft(
    filename = "DNALigation.hso",
    plateList = [
        "Empty",
        "Empty",
        "TipBox.50uL.Axygen-EV-50-R-S.tealbox",
        "Plate.96.Corning-3635.ClearUVAssay", #Working plate -empty at start
        "Plate.96.Corning-3635.ClearUVAssay",#Competent cells-full plate
        "Plate.96.Corning-3635.ClearUVAssay",#DNA ligation -full plate
        "Empty",
        "Empty",
    ],
)
#Aspirate and dispense DNA ligation
for i in range(1,13):
    soloSoft.getTip("Position3")
    soloSoft.aspirate(
        position = "Position6",
        aspirate_volumes = Plate_96_Corning_3635_ClearUVAssay().setColumn(i, 2),
        aspirate_shift = [0, 0, 2],
        mix_at_start = True,
        mix_cycles = mixCycles,
        mix_volume = mixVolumeAspirateDNALigation,
        dispense_height = dispenseHeight,
        syringe_speed = syringeSpeed,
    )

    soloSoft.dispense(
        position = "Position4",
        dispense_volumes = Plate_96_Corning_3635_ClearUVAssay().setColumn(i, 2),
        dispense_shift = [0, 0, 2],
        mix_at_finish = True,
        mix_cycles = mixCycles,
        mix_volume = mixVolumeDispenseDNALigation,
        aspirate_height = aspirateHeight,
        syringe_speed = syringeSpeed,
    )
soloSoft.shuckTip()
soloSoft.savePipeline() # saves as a hso file
 # need to break steps because it can handle only 71 steps
#----------------------------------------------------------------------------------
# add all steps to softlinx protocol
softLinx = SoftLinx("Transformation", "Transformation.slvp") # display name, path to saves
softLinx.setPlates(
    {"SoftLinx.PlateCrane.Stack5":"Plate.96.Corning-3635.ClearUVAssay",
    "SoftLinx.PlateCrane.Stack4":"TipBox.50uL.Axygen-EV-50-R-S.tealbox"
    }
)
# Move plate from stack onto deck using plate crane
softLinx.plateCraneMovePlate(["SoftLinx.PlateCrane.Stack5"],["SoftLinx.Solo.Position4"],poolID = 5) #mention poolID=stack from where you get it
softLinx.plateCraneRemoveLid(["SoftLinx.Solo.Position4"],["SoftLinx.PlateCrane.LidNest2"])

# Move the tip box from stack to deck
softLinx.plateCraneMovePlate(["SoftLinx.PlateCrane.Stack4"],["SoftLinx.Solo.Position3"],poolID = 4)
softLinx.soloSoftResetTips(3) # softlinx is telling Solo where the tips are
softLinx.plateCraneMoveCrane("SoftLinx.PlateCrane.Safe")
softLinx.soloSoftRun("CompetentCells.hso")# put the path for the file (.hso, .slvp)
softLinx.plateCraneMovePlate(["SoftLinx.Solo.Position3"],["SoftLinx.PlateCrane.Stack3"],poolID = 3) #remove the empty tip TipBox
softLinx.plateCraneMovePlate(["SoftLinx.PlateCrane.Stack4"],["SoftLinx.Solo.Position3"],poolID = 4) #putting a new tip box
softLinx.soloSoftResetTips(3)
softLinx.plateCraneMoveCrane("SoftLinx.PlateCrane.Safe")
softLinx.soloSoftRun("DNALigation.hso")
softLinx.plateCraneMovePlate(["SoftLinx.Solo.Position3"],["SoftLinx.PlateCrane.Stack3"],poolID = 3) #remove the empty tip TipBox

# move to stack2 for cooling
#liquid handling -

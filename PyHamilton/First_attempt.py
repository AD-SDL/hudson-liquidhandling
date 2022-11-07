'''
Steps:
    Defintions:

    preparing the final assay
       set plates
        transferring from cells to assay
            aspirate from cell plate
            dispense assay plate
        shuck tips
        transferring from dilution to assay
            aspirate from dilution plate
            dispense into assy
            mix
            shuck tips
        carry assay to hidex

'''

from liquidhandling import SoftLinx, SoloSoft
from liquidhandling import *

assay = "Position4"
cells = "Position5"
tips = "Position3"
dilution = "Position6"
stockCNP = "Position1"
# volume=
# mixCycles = 
# mixVolume = 
dispenseHeight = 2
aspirateHeight = 2
syringeSpeed = 50
plate_list= [
        "Empty",
        "Empty",
        "TipBox.50uL.Axygen-EV-50-R-S.tealbox",
        "Plate.96.Corning-3635.ClearUVAssay", 
        "Empty",
        "Plate.96.Corning-3635.ClearUVAssay",
        "Plate.96.Corning-3635.ClearUVAssay" #actually liquid wast,
        "Empty",
       
    ]



def transfer_cell_assay():
    '''
    Transfers cells from the cell plate to the final assay plate
    '''

    for c in np.arange(1,13,2):
    soloSoft = SoloSoft(
    filename = "cells_assay"+str(c)+".hso",
    plateList = plate_list,
    )
        for i in range(c,c+2):
            soloSoft.getTip(tips)
            
            soloSoft.aspirate(
                position = cells,
                aspirate_volumes = Plate_96_Corning_3635_ClearUVAssay().setColumn(i, x),
                aspirate_shift = [0, 0, 2],
        #         mix_at_start = True,
        #         mix_cycles = mixCycles,
        #         mix_volume = mixVolumeAspirateCompetent,
                dispense_height = dispenseHeight,
                syringe_speed = syringeSpeed,
            )

            soloSoft.dispense(
                position = assay,
                dispense_volumes = Plate_96_Corning_3635_ClearUVAssay().setColumn(i, x),
                dispense_shift = [0, 0, 2],
                # mix_at_finish = True,
                # mix_cycles = mixCycles,
                # mix_volume = mixVolume,
                aspirate_height = aspirateHeight,
                syringe_speed = syringeSpeed,
            )
        #don't even need this but just incase
        if c == 11:
            soloSoft.shuckTip
        soloSoft.savePipeline()




def transfer_dilution_assay():
    '''
    Transfers volumes from the dilution plate to the final assay plate
    '''
    for c in np.arange(1,13,2):
        soloSoft = SoloSoft(
        filename = "dilution_assay"+str(c)+".hso",
        plateList = plate_list,
        )
        for i in range(c,c+2):
            soloSoft.getTip(tips)
            
            soloSoft.aspirate(
                position = dilution,
                aspirate_volumes = Plate_96_Corning_3635_ClearUVAssay().setColumn(i, x),
                aspirate_shift = [0, 0, 2],
        #         mix_at_start = True,
        #         mix_cycles = mixCycles,
        #         mix_volume = mixVolumeAspirateCompetent,
                dispense_height = dispenseHeight,
                syringe_speed = syringeSpeed,
            )

            soloSoft.dispense(
                position = assay,
                dispense_volumes = Plate_96_Corning_3635_ClearUVAssay().setColumn(i, x),
                dispense_shift = [0, 0, 2],
                mix_at_finish = True,
                mix_cycles = mixCycles,
                mix_volume = mixVolume,
                aspirate_height = aspirateHeight,
                syringe_speed = syringeSpeed,
            )
            soloSoft.shuckTip
        
        soloSoft.savePipeline()
def preparing_finalAssay():
    
    transfer_cells_assay()
    transfer_dillution_assay()

    softLinx = SoftLinx("First_attempt", "First_attempt.slvp") # display name, path to saves
    #softLinx.setPlates(...)
    softLinx.setPlates({"SoftLinx.Solo."+assay: "Plate_96_Corning_3635_ClearUVAssay"})
    for c in np.arange(1,13,2):
        softLinx.soloSoftRun("cells_assay"+str(c)+".hso")
    for c in np.arange(1,13,2):
        softLinx.soloSoftRun("dilution_assay"+str(c)+".hso")
    

    softLinx.plateCraneMovePlate(["SoftLinx.Solo."+assay],["SoftLinx.Hidex.Nest"]) #mention poolID=stack from where you get it

    #plate crane save#
    softLinx.plateCraneMoveCrane("SoftLinx.PlateCrane.Safe")
    #save protocol file#
    softLinx.saveProtocol()


"""
!NOTE: Not enough application memory in SoloSoft to load this entire protocol -> use the .jpynb version
TODO: add notes on how to use this file
"""

from liquidhandling import SoloSoft, SoftLinx
from liquidhandling import *   # replace with tip types you end up using

#* Program Variables ------------------
media_aspirate_column = 1

stock_start_column = 1
first_column_transfer_volume = 100
dilution_media_volume = 90
dilution_transfer_volume = 10
stock_mix_volume = 70
dilution_mix_volume = 60
num_mixes = 5

default_z_shift = 2

spot_z_shift = 5
spot_volume = 3.5
#* -------------------------------------

soloSoft = SoloSoft(
    filename="dilute_then_spot.hso", 
    plateList=[
        "TipBox.200uL.Corning-4864.orangebox",
        "Empty",
        "Reservoir.12col.Agilent-201256-100.BATSgroup",
        "Empty",
        "Plate.96.Corning-3635.ClearUVAssay",
        "Plate.96.Corning-3635.ClearUVAssay",
        "TipBox.50uL.Axygen-EV-50-R-S.tealbox",
        "AgarPlate.40mL.OmniTray-242811.ColonyPicker",
    ]
)

#*Dispense diluent into full plate
    # for now, fill each half of the plate with a different media well and have becca check/refill it between runs. 
soloSoft.getTip()  
for i in range(1,13):   
    if i == 7:
        media_aspirate_column += 1  # switch to new media row for the second half of the plate
    soloSoft.aspirate(
        position="Position3", 
        aspirate_volumes=Reservoir_12col_Agilent_201256_100_BATSgroup().setColumn(media_aspirate_column, dilution_media_volume), 
        aspirate_shift=[0,0,4], 
    )
    soloSoft.dispense(
        position="Position6", 
        dispense_volumes=Plate_96_Corning_3635_ClearUVAssay().setColumn(i, dilution_media_volume), 
        dispense_shift=[0,0,default_z_shift],
    )

#* Serial Dilute into dilution plate ans spot onto agar plate
for i in range(1,3):  # loop once for each half of the plate
    
    # Prepare first column of serial dilution plate -> pure stock in first column, no dilution (100uL transfer volume)
    soloSoft.getTip() # 200uL tips
    soloSoft.aspirate(
        position="Position5", 
        aspirate_volumes=Plate_96_Corning_3635_ClearUVAssay().setColumn(stock_start_column, first_column_transfer_volume),
        aspirate_shift=[0,0,default_z_shift], 
        mix_at_start=True, 
        mix_volume=stock_mix_volume, 
        mix_cycles=num_mixes, 
        dispense_height=default_z_shift, 
    )
    soloSoft.dispense(
        position="Position6", 
        dispense_volumes=Plate_96_Corning_3635_ClearUVAssay().setColumn((6*(i-1))+1, first_column_transfer_volume),
        dispense_shift=[0,0,default_z_shift], 
        mix_at_finish=True,
        mix_volume=dilution_mix_volume, 
        mix_cycles=num_mixes,
        aspirate_height=default_z_shift, 
    )

    # LOOP: spot dilution onto agar plate and complete next dilution in serial dilution plate
    for j in range(1,6): # 1,2,3,4,5
        soloSoft.getTip("Position7")

        # spot 3.5uL onto agar plate 
        soloSoft.aspirate(
            position="Position6", 
            aspirate_volumes=Plate_96_Corning_3635_ClearUVAssay().setColumn((6*(i-1))+j, spot_volume), 
            aspirate_shift=[0,0,default_z_shift], 
        )
        soloSoft.dispense(
            position="Position7",
            dispense_volumes=AgarPlate_40mL_OmniTray_242811_ColonyPicker().setColumn((6*(i-1))+j, spot_volume),
            dispense_shift=[0,0,spot_z_shift], 
        )

        # use same tips to create the next dilution
        soloSoft.aspirate(
            position="Position6",
            aspirate_volumes=Plate_96_Corning_3635_ClearUVAssay().setColumn((6*(i-1))+j, dilution_transfer_volume), 
            aspirate_shift=[0,0,default_z_shift],
        )
        soloSoft.dispense(
            position="Position6",
            dispense_volumes=Plate_96_Corning_3635_ClearUVAssay().setColumn((6*(i-1))+j+1, dilution_transfer_volume), 
            dispense_shift=[0,0,default_z_shift], 
            mix_at_finish=True,
            mix_cycles=num_mixes,
            mix_volume=dilution_mix_volume, 
            aspirate_height=default_z_shift, 
        )
        
    # spot the last column onto the agar plate
    soloSoft.aspirate(
        position="Position6",
        aspirate_volumes=Plate_96_Corning_3635_ClearUVAssay().setColumn((6*(i-1))+6, spot_volume), 
        aspirate_shift=[0,0,default_z_shift], 
    )
    soloSoft.dispense(
        position="Position7", 
        dispense_volumes=AgarPlate_40mL_OmniTray_242811_ColonyPicker().setColumn((6*(i-1))+6, spot_volume),
        dispense_shift=[0,0,spot_z_shift], 
    )

    # make sure you draw from the next stock column for the next half of the plate
    stock_start_column +=1 

# dipsense tips and save the protocol to a .hso file
soloSoft.shuckTip()
soloSoft.savePipeline()






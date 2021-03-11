"""
Campaign 2, Day 2

Steps: 
1.) Add lysis buffer (w/ FDGlu) from well in 12 channel reservoir to each well in Corning BlackwClearBottomAssay (cells from Hidex incubation)
    output = day2_step1_AddLysisBuffer.hso


WILL INCUBATE IN HIDEX FOR 21 HOURS FOLLOWING COMPLETION OF THIS PROTOCOL

Deck Layout:
1 -> TipBox.200uL.Corning-4864.orangebox
2 -> Empty (HEAT NEST)
3 -> Reservoir.12col.Agilent-201256-100.BATSgroup
4 -> Plate.96.Corning-3635.ClearUVAssay    (same measurements as Corning Black UV)
5 -> Plate.96.PlateOne-1833-9600.ConicalBottomStorage
6 -> Plate.96.PlateOne-1833-9600.ConicalBottomStorage
7 -> TipBox.50uL.Axygen-EV-50-R-S.tealbox
8 -> Empty
"""

from liquidhandling import SoloSoft, SoftLinx
from liquidhandling import Reservoir_12col_Agilent_201256_100_BATSgroup
from liquidhandling import Plate_96_PlateOne_1833_9600_ConicalBottomStorage
from liquidhandling import Plate_96_Corning_3635_ClearUVAssay

#* Program Variables
lysis_12_channel_column = 12
lysis_transfer_volume = 22.2
lysis_syringe_speed = 25
lysis_blowoff = 0
reservoir_z_shift = .5  # tested with lysis buffer, working
dispense_z_shift = 2

#* Initialize solosoft and deck layout 
soloSoft = SoloSoft(
    filename="day2_step1_AddLysisBuffer.hso", 
    plateList=[
        "TipBox.200uL.Corning-4864.orangebox", 
        "Empty", 
        "Reservoir.12col.Agilent-201256-100.BATSgroup", 
        "Plate.96.Corning-3635.ClearUVAssay", 
        "Plate.96.PlateOne-1833-9600.ConicalBottomStorage", 
        "Plate.96.PlateOne-1833-9600.ConicalBottomStorage", 
        "TipBox.50uL.Axygen-EV-50-R-S.tealbox", 
        "Empty"
    ]
)

#* STEP 1: Add Lysis Buffer from 12 channel reservoir to cell plate 
for i in range (1,13):
    soloSoft.getTip()  # 200uL ok to aspirate 22.2 uL, NEED NEW TIP FOR EACH TRANSFER
    soloSoft.aspirate(
        position="Position3", 
        aspirate_volumes=Reservoir_12col_Agilent_201256_100_BATSgroup().setColumn(lysis_12_channel_column, lysis_transfer_volume), 
        aspirate_shift=[0,0,reservoir_z_shift], 
        pre_aspirate=lysis_blowoff,
        syringe_speed=lysis_syringe_speed,
        # mix lysis buffer before transfer? -> might cause bubbles...
    )
    soloSoft.dispense(
        position="Position4", 
        dispense_volumes=Plate_96_Corning_3635_ClearUVAssay().setColumn(i, lysis_transfer_volume), 
        dispense_shift=[0,0,dispense_z_shift], 
        blowoff=lysis_blowoff,
        syringe_speed=lysis_syringe_speed,
    )

soloSoft.shuckTip()
soloSoft.savePipeline() 

# add .hso file to SoftLinx .slvp file 
softLinx = SoftLinx("day2_step1_AddLysisBuffer", "day2_step1_AddLysisBuffer.slvp")
softLinx.soloSoftRun("C:\\Users\\svcaibio\\Dev\\liquidhandling\\example\\campaign2\\day2_step1_AddLysisBuffer.hso")  
softLinx.saveProtocol() 












"""
Campaign 2, Day 1

Steps: 
1.) Transfer bacteria from 12 channel reservoir to Corning BlackwClearBottomAssay
    output = day1_step1_TransferCells.hso
2.) Create muconate dilutions on PlateOne ConicalBottomStorage from muconate stock and buffer in 12 channel reservoir 
    output = day1_step2_DiluteMuconate.hso
3.) Add 10uL glucose dilutions and 10uL muconate dilutions to Corning BlackwClearBottomAssay plate already containing cells
    output = day1_step3_CombineCellsGlucoseMuconate.hso

WILL INCUBATE IN HIDEX FOR 21 HOURS FOLLOWING COMPLETION OF THIS PROTOCOL

Deck Layout:
1 -> TipBox.200uL.Corning-4864.orangebox
2 -> Empty (HEAT NEST)
3 -> Reservoir.12col.Agilent-201256-100.BATSgroup
        Columns 1,2 -> cells
        Column 6 -> Muconate stock (50nm)
        Column 7 -> Buffer for Muconate Dilutions
        (eventually) Column 12 -> lysis byffer (add just before runnig day 2 protocol)
4 -> Plate.96.Corning-3635.ClearUVAssay    (same measurements as Corning Black UV)
        Empty at start, will be final assay plate
5 -> Plate.96.PlateOne-1833-9600.ConicalBottomStorage
        Empty at start, Muconate Dilution plate
6 -> Plate.96.PlateOne-1833-9600.ConicalBottomStorage
        Glucose Dilution Plate
7 -> TipBox.50uL.Axygen-EV-50-R-S.tealbox
8 -> Empty
"""

from liquidhandling import SoloSoft, SoftLinx
from liquidhandling import Reservoir_12col_Agilent_201256_100_BATSgroup
from liquidhandling import Plate_96_PlateOne_1833_9600_ConicalBottomStorage
from liquidhandling import Plate_96_Corning_3635_ClearUVAssay

#* Program Variables
default_z_shift = 2

# Step 1 variables  
    # mix before transfer? -> might be a good idea
cell_transfer_volume = 180
cell_aspirate_z_shift = 4
cell_blowoff = 0
cell_mix_volume = 150
cell_num_mixes = 3

# Step 2 variables 
muconate_dilution_volumes = [84, 78, 72, 66, 60, 54, 48, 42, 36, 30, 24]  # last column excluded (can't aspirate 0uL)
muconate_12_channel_column = 7
muconate_blowoff = 0

buffer_dilution_volumes = [66, 72, 78, 84, 90, 96, 102, 108, 114, 120, 126, 150]
buffer_12_channel_column = 6
buffer_blowoff = 0

dilution_mix_volume = 80
dilution_num_mixes = 3

# Step 3 Variables 
glucose_transfer_volume = 10
glucose_blowoff = 0
glucose_z_shift = 1

muconate_transfer_volume = 10
muconate_blowoff = 0
step3_mix_volume = 50
step3_num_mixes = 3

#* Initialize solosoft and deck layout 
soloSoft = SoloSoft(
    filename="day1_step1_TransferCells.hso", 
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

#* STEP 1: Transfer Cells ------------------------------------------------------------
soloSoft.getTip()   # 200uL tips -> all transfers are same cells, OK to keep same tips for all of step 1
for i in range(1,3):
    for j in range(1,7):
        soloSoft.aspirate(  
            position="Position3", 
            aspirate_volumes=Reservoir_12col_Agilent_201256_100_BATSgroup().setColumn(i, cell_transfer_volume), 
            aspirate_shift=[0,0,cell_aspirate_z_shift], 
            pre_aspirate=cell_blowoff,
            mix_at_start=True,              # mix cells before aspirating them -> probably a good idea
            mix_volume=cell_mix_volume,
            mix_cycles=cell_num_mixes, 
            dispense_height = cell_aspirate_z_shift,
        )
        soloSoft.dispense(
            position="Position4", 
            dispense_volumes=Plate_96_Corning_3635_ClearUVAssay().setColumn((6*(i-1))+j, cell_transfer_volume), 
            dispense_shift=[0,0,default_z_shift], 
            blowoff=cell_blowoff, 
            # no need to mix because it will shake in the Hidex
        )

        # for testing
        # j_column = (6*(i-1))+j
        # print("Cell spirate: 12 channel ( " + str(i)  + " ) to BlackwClearBottomAssay ( " + str(j_column) + " )") 

soloSoft.shuckTip()
soloSoft.savePipeline()

#* STEP 2: Create Muconate Dilution plate -----------------------------------------------

soloSoft = SoloSoft(
    filename="day1_step2_DiluteMuconate.hso", 
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

# Dispense buffer into whole dilution plate
soloSoft.getTip()  # 200uL tips 
for i in range(1,13):
    soloSoft.aspirate(
        position="Position3", 
        aspirate_volumes=Reservoir_12col_Agilent_201256_100_BATSgroup().setColumn(buffer_12_channel_column, buffer_dilution_volumes[i-1]), 
        aspirate_shift=[0,0,default_z_shift], 
        pre_aspirate=buffer_blowoff, 
    )
    soloSoft.dispense(
        position="Position5", 
        dispense_volumes=Plate_96_PlateOne_1833_9600_ConicalBottomStorage().setColumn(i, buffer_dilution_volumes[i-1]), 
        aspirate_height=default_z_shift, 
        blowoff=buffer_blowoff, 
    )
# dispense muconate into whole dilution plate, no need to get new tips here
for i in range(1,12):
    soloSoft.aspirate(
        position="Position3", 
        aspirate_volumes=Reservoir_12col_Agilent_201256_100_BATSgroup().setColumn(muconate_12_channel_column, muconate_dilution_volumes[i-1]), 
        aspirate_shift=[0,0,default_z_shift], 
        pre_aspirate=buffer_blowoff, 
    )
    soloSoft.dispense(
        position="Position5", 
        dispense_volumes=Plate_96_PlateOne_1833_9600_ConicalBottomStorage().setColumn(i, muconate_dilution_volumes[i-1]), 
        dispense_shift=[0,0,default_z_shift],
        blowoff=buffer_blowoff,
        mix_at_finish=True, 
        mix_volume=dilution_mix_volume, 
        mix_cycles=dilution_num_mixes, 
        aspirate_height=default_z_shift
        # no need to mix, will shake in Hidex 
    )
soloSoft.shuckTip()
soloSoft.savePipeline()

#* STEP 3: Combine muconate and glucose with cell plate -> New tips each transfer! -------------------
soloSoft = SoloSoft(
    filename="day1_step3_CombineCellsGlucoseMuconate.hso", 
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

for i in range(1,13):
    # dispense glucose into cell plate 
    soloSoft.getTip("Position7")
    soloSoft.aspirate(
        position="Position6", 
        aspirate_volumes=Plate_96_PlateOne_1833_9600_ConicalBottomStorage().setColumn(i, glucose_transfer_volume), 
        aspirate_shift=[0,0,glucose_z_shift], 
        pre_aspirate=glucose_blowoff,
        mix_at_start=True, 
        mix_volume=step3_mix_volume, 
        mix_cycles=step3_num_mixes,
        dispense_height=default_z_shift, # change this dispense height to match glucose_z_shift
    )
    soloSoft.dispense(
        position="Position4", 
        dispense_volumes=Plate_96_Corning_3635_ClearUVAssay().setColumn(i, glucose_transfer_volume), 
        dispense_shift=[0,0,default_z_shift], 
        blowoff=glucose_blowoff,
    )

    # dispense muconate into cell plate
    soloSoft.aspirate(
        position="Position5", 
        aspirate_volumes=Plate_96_PlateOne_1833_9600_ConicalBottomStorage().setColumn(i, muconate_transfer_volume), 
        aspirate_shift=[0,0,default_z_shift], 
        pre_aspirate=muconate_blowoff,
        mix_at_start=True,
        mix_volume=step3_mix_volume,
        mix_cycles=step3_num_mixes,
        dispense_height=default_z_shift,
    )
    soloSoft.dispense(
        position="Position4", 
        dispense_volumes=Plate_96_Corning_3635_ClearUVAssay().setColumn(i, muconate_transfer_volume), 
        dispense_shift=[0,0,default_z_shift], 
        blowoff=muconate_blowoff,
        # no need to mix -> will shake in the Hidex
    )
    
soloSoft.shuckTip()
soloSoft.savePipeline()

#* Add Steps 1-3 .hso files to SofltLinx .slvp file (and generate .ahk and manifest .txt files)
softLinx = SoftLinx("day1_cells_glucose_muconate", "day1_cells_glucose_muconate.slvp")
softLinx.soloSoftRun("C:\\Users\\svcaibio\\Dev\\liquidhandling\\example\\campaign2\\day1_step1_TransferCells.hso")  # add the correct paths of the .hso files 
softLinx.soloSoftRun("C:\\Users\\svcaibio\\Dev\\liquidhandling\\example\\campaign2\\day1_step2_DiluteMuconate.hso")      # assume transfered from lambda 6 or run locally for prep on hudson01? 
softLinx.soloSoftRun("C:\\Users\\svcaibio\\Dev\\liquidhandling\\example\\campaign2\\day1_step3_CombineCellsGlucoseMuconate.hso") 
softLinx.saveProtocol() 


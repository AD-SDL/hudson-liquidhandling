import argparse
import os
from re import L
import sys
import time
from subprocess import Popen
from liquidhandling import SoloSoft
from liquidhandling import SoftLinx
from liquidhandling import Reservoir_12col_Agilent_201256_100_BATSgroup
from liquidhandling import Plate_96_Corning_3635_ClearUVAssay

"""
DNA ASSEMBLY
 
SOLO DECK ARRANGEMENT AT START: 
Pos 1 = EMPTY
Pos 2 = EMPTY (heat nest)
Pos 3 = 50uL tips (filter tips if possible)
Pos 4 = EMPTY AT START (later 96 well clear, flat-bottom plate w/ lid placed by Plate Crane)
Pos 5 = EMPTY
Pos 6 = EMPTY AT START (later 96 well clear, flat-bottom plate w/ lid placed by Plate Crane)
Pos 7 = EMPTY
Pos 8 = EMPTY

Post Transformation Steps: 
"""

def generate_post_transformation(): 

    # file paths
    #instruction_file_directory = "C:\\labautomation\\instructions"
    #instruction_file_directory = "C:\\Users\\svcaibio\\Desktop\\FOR_BEN"
    instruction_file_directory = "C:\\Users\\svcaibio\\Desktop\\Debug\\post_transformation"
    transf_to_sel_filename = os.path.join(instruction_file_directory, "transf_to_sel.hso")
    sel_to_sel_filename = os.path.join(instruction_file_directory, "sel_to_sel.hso")
    sel_to_master_filename = os.path.join(instruction_file_directory, "sel_to_master.hso")
    master_to_overnight_filename = os.path.join(instruction_file_directory, "master_to_overnight.hso")
    overnight_to_test_filename = os.path.join(instruction_file_directory, "overnight_to_test.hso")

    # plate types
    transformation_plate_type = "Plate_96_Corning_3635_ClearUVAssay"
    selection_plate_type = "Plate_96_Corning_3635_ClearUVAssay"
    master_plate_type = "Plate_96_Corning_3635_ClearUVAssay"
    overnight_plate_type = "Plate_96_Corning_3635_ClearUVAssay"
    test_plate_type = "Plate_96_Corning_3635_ClearUVAssay"

    # z shift

    # default variables 
    flat_96_z_shift = 2  # changed from 1 TEST 
    default_num_mix = 3
    default_mix_volume = 45 # using 50 uL tips TEST 

    # transformation plate to selection plate variables (transformation plate -> selection plate #1)
    transf_plate_wells = ["A1", "A2", "A3", "A4", "A5", "A6", "A7", "A8", "A9", "A10", "A11", "A12"]
    sel_plate_wells = transf_plate_wells.copy()
    transf_plate_asp_volume_step_1 = 10
    transf_plate_mix_volume_step_1 = 45 # using 50uL tips 
    sel_plate_mix_volume_step_1 = 45 
    num_mix_step_1 = 3

    # selection plate to selection plate variables
    sel_to_sel_asp_volume = 2 # check that this can even be done...
    # keep the other variables the same as step 1

    # step 4 variables (selection plate #3 -> master/freezer plate)
    sel_to_master_asp_volume = 100 # do in 2 transfers, using 50uL tips!

    # step 5 variables (master/freezer plate -> overnight plate)
    master_to_overnight_asp_volume = 10

    # step 6 variables (overnight/freezer plate -> test plate)
    overnight_to_test_asp_volume = 2

    # Hidex assay variables 
    hidex_assay_name = "Campaign1_noIncubate2"  # TODO --> make Hidex protocol in app
    num_readings = 6  # total, including T0 reading
    

    # #incubation times
    # default_incubation_time = [0,3,0,0]  # --> 0 days, 3 hours, 0 minutes, 0 seconds 
    # overnight_incubation_time = [0,8,0,0]  # --> 0 days, 8 hours, 0 minutes, 0 seconds
    # incubation_time_between_readings = [0,1,0,0] # 0 days, 1 hour, 0 mintues, 0 seconds

    # FOR TESTING
    default_incubation_time = [0,0,0,10]  # --> 0 days, 0 hours, 0 minutes, 10 seconds 
    overnight_incubation_time = [0,0,0,20] #  --> 0 days, 0 hours, 0 minutes, 20 seconds
    incubation_time_between_readings = [0,0,0,5] # 0 days, 0 hours, 0 minutes, 5 seconds


    #* SOFTLINX .slvp PROTOCOL - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    softLinx = SoftLinx("Post Transformation", "C:\\Users\\svcaibio\\Desktop\\Debug\\post_transformation\\post_transformation.slvp")

    # initialize plates 
    softLinx.setPlates({"SoftLinx.PlateCrane.Stack5": "Plate.96.Corning-3635.ClearUVAssay"})  # assume all new plates in same stack until stack issue fixed

    """ Assume transformation plate is already in incubator with plate ID 0"""

    plate_id=1  # keep track of current plate id
    
    #* TRANSFORMATION PLATE --> SELECTION PLATE #1
    # set up SOLO deck
    set_up(current_softLinx=softLinx, incubator_plate_id=plate_id)

    # generate then run the first liquidhandling hso
    hso_1 = generate_hso(
        transf_to_sel_filename, 
        transf_plate_wells, 
        sel_plate_wells, 
        transf_plate_asp_volume_step_1, 
        num_mix_step_1, 
        transf_plate_mix_volume_step_1,
        sel_plate_mix_volume_step_1,
        flat_96_z_shift,
        flat_96_z_shift
    )
    softLinx.soloSoftRun(hso_1)
    
    # clear SOLO deck and transfer new plate to incubator
    plate_id += 1
    tear_down(current_softLinx=softLinx, incubator_plate_id=plate_id, incubation_time=default_incubation_time, shaker_speed=30)

    #* SELECTION PLATE #1 --> SELECTION PLATE #2 --> SELECTION PLATE #3
    # generate the liquidhandling hso (same for both steps)
    hso_2_and_3 = generate_hso(
        sel_to_sel_filename, 
        sel_plate_wells, 
        sel_plate_wells, 
        sel_to_sel_asp_volume, 
        default_num_mix, 
        default_mix_volume, 
        default_mix_volume, 
        flat_96_z_shift,
        flat_96_z_shift
    )
    for i in range(2): 
        # set up the SOLO deck
        set_up(current_softLinx=softLinx, incubator_plate_id=plate_id)

        # run liquidhandling hso file 
        softLinx.soloSoftRun(hso_2_and_3)

        # clear SOLO deck and move new plate to incubator
        plate_id += 1
        tear_down(current_softLinx=softLinx, incubator_plate_id=plate_id, incubation_time=default_incubation_time, shaker_speed=30)

    #* SELECTION PLATE #3 --> MASTER PLATE
    # set up the SOLO deck
    set_up(current_softLinx=softLinx, incubator_plate_id=plate_id)

    # generate and run liquidhandling hso
    hso_4 = generate_hso(
        sel_to_master_filename, 
        sel_plate_wells, 
        sel_plate_wells, 
        sel_to_master_asp_volume, 
        default_num_mix, 
        default_mix_volume,
        default_mix_volume,
        flat_96_z_shift,
        flat_96_z_shift,
    )
    softLinx.soloSoftRun(hso_4)

    #different tear down method, don't need to incubate, need to freeze potentially 
    plate_id += 1
    softLinx.plateCraneReplaceLid(["SoftLinx.PlateCrane.LidNest1"], ["SoftLinx.Solo.Position6"])
    softLinx.plateCraneMovePlate(["SoftLinx.Solo.Position6"], ["SoftLinx.PlateCrane.Stack1"])  # remove used plate to stack 
    softLinx.plateCraneReplaceLid(["SoftLinx.PlateCrane.LidNest2"], ["SoftLinx.Solo.Position4"])
    softLinx.plateCraneMovePlate(["SoftLinx.Solo.Position4"],["SoftLinx.Solo.Position6"])  # move to other deck position, now source plate
    


    #* MASTER PLATE --> OVERNIGHT PLATE
    # set up the SOLO deck (different than normal)
    softLinx.plateCraneRemoveLid(["SoftLinx.PlateCrane.Position6"], ["SoftLinx.PlateCrane.LidNest1"])  # remove lid again 

    # place prefilled media plate onto solo deck position 4, remove lid
    softLinx.plateCraneMovePlate(["SoftLinx.PlateCrane.Stack5"],["SoftLinx.Solo.Position4"])
    softLinx.plateCraneRemoveLid(["SoftLinx.Solo.Position4"],["SoftLinx.Solo.LidNest2"])
    softLinx.plateCraneMoveCrane("SoftLinx.PlateCrane.Safe")

    # generate and run liquidhandling hso
    hso_5 = generate_hso(
        master_to_overnight_filename,
        sel_plate_wells,
        sel_plate_wells,
        master_to_overnight_asp_volume,
        default_num_mix,
        default_mix_volume,
        default_mix_volume,
        flat_96_z_shift,
        flat_96_z_shift,
    )
    softLinx.soloSoftRun(hso_5)

    # clear SOLO deck and move new plate to incubator
    plate_id += 1
    tear_down(current_softLinx=softLinx, incubator_plate_id=plate_id,incubation_time=overnight_incubation_time,shaker_speed=30)



    #* OVERNIGHT PLATE --> TEST PLATE
    # set up the SOLO deck
    set_up(current_softLinx=softLinx, incubator_plate_id=plate_id)

    # generate and run the liquidhandling hso
    hso_6 = generate_hso(
        overnight_to_test_filename, 
        sel_plate_wells, 
        sel_plate_wells,
        overnight_to_test_asp_volume, 
        default_num_mix,
        default_mix_volume,
        default_mix_volume,
        flat_96_z_shift,
        flat_96_z_shift,
    )
    softLinx.soloSoftRun(hso_6)

    # clear SOLO deck and prepare for T0 Hidex reading
    softLinx.plateCraneReplaceLid(["SoftLinx.PlateCrane.LidNest1"], ["SoftLinx.Solo.Position6"])
    softLinx.plateCraneMovePlate(["SoftLinx.Solo.Position6"], ["SoftLinx.PlateCrane.Stack1"])

    #* TEST PLATE HIDEX READINGS 
    # T0 hidex reading
    softLinx.plateCraneMovePlate(["SoftLinx.Solo.Position4"],["SoftLinx.Hidex.Nest"])
    softLinx.plateCraneMoveCrane("SoftLinx.PlateCrane.Safe")
    softLinx.hidexRun(hidex_assay_name)
    #TODO send results to lambda6 automatically
    softLinx.plateCraneMovePlate(["SoftLinx.Hidex.Nest"],["SoftLinx.Liconic.Nest"])  #TODO: define Liconic.NestAfterHidex location
    softLinx.hidexClose()
    softLinx.plateCraneReplaceLid(["SoftLinx.PlateCrane.LidNest2"],["SoftLinx.Liconic.Nest"])
    softLinx.plateCraneMoveCrane("SoftLinx.PlateCrane.Safe")
    softLinx.liconicLoadIncubator(loadID=plate_id)
    softLinx.liconicShake(shaker1Speed=30, shakeTime=incubation_time_between_readings)
    
    for i in range(num_readings-1):  
        # take hidex reading
        take_hidex_reading(current_softLinx=softLinx,incubator_plate_id=plate_id,hidex_assay=hidex_assay_name)

        # if last reading complete, move used plate to stack 1 
        if i == num_readings - 2: 
            softLinx.plateCraneMovePlate(["SoftLinx.Hidex.Nest"], ["SoftLinx.PlateCrane.Stack1"])
            softLinx.hidexClose()
            softLinx.plateCraneReplaceLid(["SoftLinx.PlateCrane.LidNest2"], ["SoftLinx.PlateCrane.Stack1"])
            softLinx.plateCraneMoveCrane("SoftLinx.PlateCrane.Safe")

        # otherwise, move to incubator until next reading
        else: 
            softLinx.plateCraneMovePlate(["SoftLinx.Hidex.Nest"],["SoftLinx.Liconic.Nest"])  #TODO: define Liconic.NestAfterHidex location
            softLinx.hidexClose()
            softLinx.plateCraneReplaceLid(["SoftLinx.PlateCrane.LidNest2"],["SoftLinx.Liconic.Nest"])
            softLinx.plateCraneMoveCrane("SoftLinx.PlateCrane.Safe")
            softLinx.liconicLoadIncubator(loadID=plate_id)
            softLinx.liconicShake(shaker1Speed=30, shakeTime=incubation_time_between_readings)

    softLinx.saveProtocol()



# HELPER METHODS: ---------------------------------------------------------------
def set_up(current_softLinx:SoftLinx, incubator_plate_id): 
    """ set_up

        Descrition: Sets up SOLO deck for liquidhandling
                    Retreives specified plate from incubator and places it on SOLO position 6
                    Retreives prefilled LB plate from Stack5 and places it on SOLO position 4

        Parameters: 
            current_softLinx: the instance of SoftLinx that should add the included steps
            incubator_plate_id: plate_id corresponding to incubaotor plate to place on SOLO deck
            
    """
    # place plate from incubator on deck, remove lid
    current_softLinx.liconicUnloadIncubator(loadID=incubator_plate_id)
    current_softLinx.plateCraneMovePlate(["SoftLinx.Liconic.Nest"],["SoftLinx.Solo.Position4"])  
    current_softLinx.plateCraneRemoveLid(["SoftLinx.Solo.Position6"],["SoftLinx.PlateCrane.LidNest1"])

    # place prefilled media plate onto solo deck position 4, remove lid
    current_softLinx.plateCraneMovePlate(["SoftLinx.PlateCrane.Stack5"],["SoftLinx.Solo.Position4"])
    current_softLinx.plateCraneRemoveLid(["SoftLinx.Solo.Position4"],["SoftLinx.Solo.LidNest2"])

    current_softLinx.plateCraneMoveCrane("SoftLinx.PlateCrane.Safe")


# ---------------------------------------------------------------------------------
def tear_down(current_softLinx:SoftLinx, incubator_plate_id, incubation_time, shaker_speed=30): 
    """ tear_down
    
        Description: Clears the SOLO deck after liquidhandling is complete
                     Transfers the plate into the incubator

        Parameters:
            current_softLinx: the instance of SoftLinx that should add the included steps
            incubator_plate_id: plate_id of the newly completed plate to be placed in incubator
            incubation_time: How long the plate should incubate before next step of the protocol 
                note: must be a list of integers [days, hours, minutes, seconds] (ex. [0,3,0,0] means 3 hours)
            shaker_speed: shaker setting for incubator. Must be 1-50. (20 = 200 rpm, 30 = 300 rpm, etc.)
    
    """
    # remove used origin plate from deck and place in stack 1
    current_softLinx.plateCraneReplaceLid(["SoftLinx.PlateCrane.LidNest1"], ["SoftLinx.Solo.Position6"])
    current_softLinx.plateCraneMovePlate(["SoftLinx.Solo.Position6"], ["SoftLinx.PlateCrane.Stack1"])

    # replace lid on new plate and move to incubator nest 
    current_softLinx.plateCraneReplaceLid(["SoftLinx.PlateCrane.LidNest2"], ["SoftLinx.Solo.Position4"])
    current_softLinx.plateCraneMovePlate(["SoftLinx.Solo.Position4"],["SoftLinx.Liconic.Nest"])
    current_softLinx.plateCraneMoveCrane("SoftLinx.PlateCrane.Safe")

    # load the new plate into the incubator
    current_softLinx.liconicLoadIncubator(loadID=incubator_plate_id)
    current_softLinx.liconicShake(shaker1Speed=shaker_speed, shakeTime=incubation_time)


# ----------------------------------------------------------------------------------
def take_hidex_reading(current_softLinx:SoftLinx, incubator_plate_id, hidex_assay): 
    """ take_hidex_reading

        Description: Removes the specified plate (plate_id) from incubator and transfers to Hidex
                     Runs desired Hidex assay (hidex_assay) to collect data on plate
                     TODO Transfers data to Lambda6 for quality control and processing

        Parameters: 
            current_softLinx: the instance of SoftLinx that should add the included steps
            incubator_plate_id: plate_id of the newly completed plate to be placed in incubator
            hidex_assay: string name of assay protocol name on Hidex app (on hudson01) that you wish to run

    """
    # remove specified plate from incubator
    current_softLinx.liconicUnloadIncubator(loadID=incubator_plate_id)

    # remove lid and transfer to Hidex
    current_softLinx.plateCraneRemoveLid(["SoftLinx.Liconic.Nest"],["SoftLinx.LidNest2"])
    current_softLinx.plateCraneMovePlate(["SoftLinx.Liconic.Nest"],["SoftLinx.Hidex.Nest"])
    current_softLinx.plateCraneMoveCrane("SoftLinx.PlateCrane.Safe")

    # take Hidex reading
    current_softLinx.hidexRun(hidex_assay)

    #TODO transfer readings back to lambda6 automatically

# ----------------------------------------------------------------------------------
def generate_hso(file_path, origin_wells, destination_wells, volume, num_mix, origin_mix_volume, destination_mix_volume, origin_z_shift, destination_z_shift):
    """ generate_delection_hso

        Description: Generates the SOLO .hso files for creating the selection plates

        Parameters:
            filename: filepath to sa
            origin_wells: list of wells in origin plate to aspirate from (ex. ["A1", "A2", "A3", ...])
            destination_wells: list of wells in destination plate to dispense into (ex. ["B1", "B2", "B3", ...])
                note: in the above examples, A1 -> B1, A2 -> B2, A3 -> B3. Both lists must be same length
            volume: volume of liquid to transfer from origin to destination
            num_mix: 
            origin_mix_volume: mix volume before aspiration
            destination_mix_volume: mix volume after dispense 
            origin_z_shift: distance from well bottom (mm) to aspirate
            destination_z_shift: distance from well bottom (mm) to dispense
    
    """
    two_transfers = False 
    if volume > 50: 
        volume = float(volume)/float(2)
        two_transfers = True

    soloSoft = SoloSoft(
        filename=file_path,
        plateList=[
            "Empty",
            "Empty",
            "TipBox.50uL.Axygen-EV-50-R-S.tealbox", #TODO: do we have 20uL tips? 
            "Plate.96.Corning-3635.ClearUVAssay",
            "Empty",
            "Plate.96.Corning-3635.ClearUVAssay",
            "Empty",
            "Empty",
        ],
    )
    
    for i in range(len(origin_wells)): 
        soloSoft.getTip("Position3", num_tips=1)
        soloSoft.aspirate(
            position="Position6", 
            aspirate_volumes=Plate_96_Corning_3635_ClearUVAssay().setCell(origin_wells[i][0], int(origin_wells[i][1:]), volume),
            aspirate_shift=[0,0,origin_z_shift], 
            mix_at_start=True, 
            mix_cycles=num_mix, 
            mix_volume=origin_mix_volume,
            dispense_height=origin_z_shift,
        )
        soloSoft.dispense(
            position="Position4", 
            dispense_volumes=Plate_96_Corning_3635_ClearUVAssay().setCell(destination_wells[i][0], int(destination_wells[i][1:]), volume),
            dispense_shift=[0,0,destination_z_shift],
            mix_at_finish=True, 
            mix_cycles=num_mix, 
            mix_volume=destination_mix_volume, 
            aspirate_height=destination_z_shift,
        )

        if two_transfers == True: # repeat the above transfers again to transfer total volume
            soloSoft.aspirate(
                position="Position6", 
                aspirate_volumes=Plate_96_Corning_3635_ClearUVAssay().setCell(origin_wells[i][0], int(origin_wells[i][1:]), volume),
                aspirate_shift=[0,0,origin_z_shift], 
                mix_at_start=True, 
                mix_cycles=num_mix, 
                mix_volume=origin_mix_volume,
                dispense_height=origin_z_shift,
            )
            soloSoft.dispense(
                position="Position4", 
                dispense_volumes=Plate_96_Corning_3635_ClearUVAssay().setCell(destination_wells[i][0], int(destination_wells[i][1:]), volume),
                dispense_shift=[0,0,destination_z_shift],
                mix_at_finish=True, 
                mix_cycles=num_mix, 
                mix_volume=destination_mix_volume, 
                aspirate_height=destination_z_shift,
            )

    soloSoft.shuckTip()
    soloSoft.savePipeline()
    
    return file_path


# ----------------------------------------------------------------------------------
def main(args):
    # pass to method
    generate_post_transformation()

# ----------------------------------------------------------------------------------
if __name__ == "__main__":
    # execute only if run as a script
    main(sys.argv)
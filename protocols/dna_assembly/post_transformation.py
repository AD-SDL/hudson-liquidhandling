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
from tip_utils import replace_tip_box, remove_tip_box
 
"""
DNA ASSEMBLY

TODO: rewrite this

USAGE EXAMPLE: python post_transformation.py -t 
 
SOLO DECK ARRANGEMENT AT START: 
Pos 1 = EMPTY
Pos 2 = EMPTY (heat nest)
Pos 3 = 50uL tips (filter tips if possible)
Pos 4 = EMPTY AT START (later 96 well clear, flat-bottom plate w/ lid placed by Plate Crane)
Pos 5 = EMPTY
Pos 6 = EMPTY AT START (later 96 well clear, flat-bottom plate w/ lid placed by Plate Crane)
Pos 7 = EMPTY
Pos 8 = EMPTY

POST TRANSFORMATION STEPS: 
*** start with transformation plate in incubator, with incubator plate ID = 1 ***

Transformation plate to selection plate #1 
- Unload transformation plate from incubator --> SOLO position 6
- Move new plate to SOLO position 4 (will be selection plate #1)
    Note: new plate will contain 180uL LB media + antobiotic in each well)
- exectue transf_to_sel.hso: 
    - transfer 10uL from each well of transformation plate to corresponding well in selection plate #1 
- Load selection plate #1 into incubator (plate ID = 2) and remove used transformation plate to Stack 1
- Incubate for 3 hours

Selection plate #1 to master plate:
- Unload selection plate #1 from incubator (plate ID = 2) --> SOLO position 6
- Move new plate to SOLO position 4 (will be master plate)
    (Note: new plate will contain 100uL of 50% glycerol media in each well)
- exectue sel_to_master.hso: 
    - transfer 100uL from each well of selection plate #1 to corresponding well in master plate  
- Load master plate into incubator, plate ID = 3
- Freeze for later use or immediately proceed to next step 
    (If proceeding, remove used selection plate #1 to Stack 1 and move master plate to SOLO position 6)

Master plate to overnight plate: 
- Unload master plate from incubator (plate ID = 3) --> SOLO position 6
- Move new plate to SOLO position 4 (will be overnight plate)
    (Note: new plate will contain 180uL LB media + antibiotic in each well)
- exectue master_to_overnight.hso: 
    - transfer 10uL from each well of master plate to corresponding well in overnight plate 
- Load overnight plate into incubator, plate ID = 4
- Incubate for 8 hours

Overnight plate to test plate: 
- Unload overnight plate from incubator (plate ID = 4) --> SOLO position 6
- Move new plate to SOLO position 4 (will be test plate)
    (Note: new plate will contain 180uL LB media + antibiotic in each well)
- exectue overnight_to_test.hso: 
    - transfer 10uL from each well of overnight plate to corresponding well in test plate 

Take Hidex Readings: 
START LOOP (6 times)
- Move test plate to Hidex (either move from SOLO Position 4 or unload from incubator)
- Run Hidex Assay 
    - TODO: details about assay
- Load test plate into incubator (except after last reading move to Stack 1)
- Incubate for 1 hour
END LOOP


"""

def generate_post_transformation(is_test): 

    # file paths
    lambda6_path = "/lambda_stor/data/hudson/instructions/"
    num_assay_plates = 1
    num_assay_wells = 96 
    assay_plate_type = "hidex"
    data_format = "dna_assembly"

    # Create directory to store all instruction files
    project = "DNA_Assembly"
    project_desc = "post_transformation"
    timestamp = str(time.time()).split(".")[0]
    directory_name = f"{project}-{project_desc}-{timestamp}"
    directory_path = os.path.join(
        os.path.realpath(os.path.dirname(lambda6_path)), directory_name
    )

    try:
        os.makedirs(directory_path, exist_ok=True)
        print(f"Protocol directory created: {directory_path}")
    except OSError as e:
        print(e)
        print(f"failed to create new directory for instructions: {directory_path}")

    # hso file paths
    transf_to_master_filename = os.path.join(directory_path, "transf_to_master.hso")
    #sel_to_sel_filename = os.path.join(instruction_file_directory, "sel_to_sel.hso")
    #sel_to_master_filename = os.path.join(directory_path, "sel_to_master.hso")
    glycerol_to_master_filename = os.path.join(directory_path, "glycerol_to_master.hso")
    master_to_overnight_filename = os.path.join(directory_path, "master_to_overnight.hso")
    overnight_to_test_filename = os.path.join(directory_path, "overnight_to_test.hso")
    softLinx_filename = os.path.join (directory_path, "post_transformation.slvp")

    # plate types
    transformation_plate_type = "Plate_96_Corning_3635_ClearUVAssay"
    selection_plate_type = "Plate_96_Corning_3635_ClearUVAssay"
    master_plate_type = "Plate_96_Corning_3635_ClearUVAssay"
    overnight_plate_type = "Plate_96_Corning_3635_ClearUVAssay"
    test_plate_type = "Plate_96_Corning_3635_ClearUVAssay"

    # z shift

    # default variables 
    flat_96_z_shift = 2  # changed from 1 
    deep_well_z_shift = 2
    default_num_mix = 3
    default_mix_volume = 45 # using 50 uL tips 

    # transformation plate to master plate variables (transformation plate -> master plate)
    transf_plate_wells = ["A1", "A2", "A3", "A4", "A5", "A6", "A7", "A8", "A9", "A10", "A11", "A12"]
    master_plate_wells = transf_plate_wells.copy()
    transf_plate_asp_volume_step_1 = 2
    transf_plate_mix_volume_step_1 = 45 # using 50uL tips (~180uL or so in wells?)
    master_plate_mix_volume_step_1 = 15 # only 52uL in wells (! tiny in flat bottom plate)
    num_mix_step_1 = 3

    # glycerol variables
    glycerol_plate_asp_volume = 100 
    glycerol_plate_mix_volume = 100
    master_plate_mix_volume = 45

    # selection plate to selection plate variables 
    #sel_to_sel_asp_volume = 2  # other variables the same as step 1

    # step 4 variables (selection plate #3 -> master/freezer plate)
    sel_to_master_asp_volume = 100 # do in 2 transfers, using 50uL tips!

    # step 5 variables (master/freezer plate -> overnight plate)
    master_to_overnight_asp_volume = 5

    # step 6 variables (overnight/freezer plate -> test plate)
    overnight_to_test_asp_volume = 2

    # Hidex assay variables 
    hidex_assay_name = "Absorbance_and_Fluorescence"  
    num_readings = 6  # total, including T0 reading
    

    #incubation times
    default_incubation_time = [0,8,0,0]  # --> 0 days, 8 hours, 0 minutes, 0 seconds 
    overnight_incubation_time_1= [0,19,0,0]  # --> 0 days, 19 hours, 0 minutes, 0 seconds
    overnight_incubation_time_2= [0,20,0,0]  # --> 0 days, 20 hours, 0 minutes, 0 seconds
    incubation_time_between_readings = [0,1,0,0] # 0 days, 1 hour, 0 mintues, 0 seconds

    # # FOR TESTING
    # default_incubation_time = [0,0,0,10]  # --> 0 days, 0 hours, 0 minutes, 10 seconds 
    # overnight_incubation_time_1 = [0,0,0,20] #  --> 0 days, 0 hours, 0 minutes, 20 seconds
    # overnight_incubation_time_2 = [0,0,0,20] #  --> 0 days, 0 hours, 0 minutes, 20 seconds
    # incubation_time_between_readings = [0,0,0,5]  #  --> 0 days, 0 hours, 0 minutes, 5 seconds


    #* SOFTLINX .slvp PROTOCOL - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    softLinx = SoftLinx("Post Transformation", softLinx_filename)

    # initialize plates # TODO test this
    softLinx.setPlates({
        "SoftLinx.PlateCrane.Stack5": "Plate.96.Corning-3635.ClearUVAssay",
        "SoftLinx.PlateCrane.Stack4": "TipBox.50uL.Axygen-EV-50-R-S.tealbox",  # will also contain a 180uL tip box (ran out of stacks to use)
    })  

    """ Assume transformation plate is already in incubator with plate ID 1"""

    plate_id=1  
    
    #* TRANSFORMATION PLATE --> MASTER PLATE
    # set up SOLO deck, get new tips and reset tip count
    set_up(current_softLinx=softLinx, incubator_plate_id=plate_id, empty_tip_deck_loc="Position3") 

    # generate then run the first liquidhandling hso
    hso_1 = generate_hso(
        transf_to_master_filename, 
        directory_name, 
        transf_plate_asp_volume_step_1, 
        num_mix_step_1, 
        transf_plate_mix_volume_step_1,
        master_plate_mix_volume_step_1,
        flat_96_z_shift,
        flat_96_z_shift, 
    )
    softLinx.soloSoftRun(hso_1)
    
    # clear SOLO deck and transfer new plate to incubator
    plate_id += 1
    tear_down(current_softLinx=softLinx, incubator_plate_id=plate_id, incubation_time=overnight_incubation_time_1, shaker_speed=30) # TODO: test this


    #* MASTER PLATE --> OVERNIGHT PLATE
    
    # set up the SOLO deck, get new 50uL tips, reset solo tip count at deck pos 3
    set_up(current_softLinx=softLinx, incubator_plate_id=plate_id, empty_tip_deck_loc="Position3") 
    
    # # generate and run liquidhandling hso(s)
    glycerol_hso = generate_glycerol_hso(   # uses 180uL tips, deck pos 5
        glycerol_to_master_filename,
        directory_name,
        glycerol_plate_asp_volume,  # 100uL 
        default_num_mix,  # 3
        glycerol_plate_mix_volume,  # 100uL 
        master_plate_mix_volume,  # 45uL 
        deep_well_z_shift, 
        flat_96_z_shift,
    )
    softLinx.soloSoftRun(glycerol_hso)  # only run once since using 180uL tips 

    # remove empty 180uL tips from deck
    remove_tip_box(
        current_softLinx=softLinx, 
        empty_tip_loc="Position3", 
        poolID=4,
    )

    # place 50uL tips on deck
    replace_tip_box(
        current_softLinx=softLinx, 
        empty_tip_loc="Position3", 
        poolID=4,
    )

    # generate and run liquidhandling hso
    hso_3 = generate_hso(
        master_to_overnight_filename,
        directory_name,
        master_to_overnight_asp_volume,  # 5uL 
        default_num_mix,  # 3
        default_mix_volume,  # 45uL 
        default_mix_volume,  # 45uL 
        flat_96_z_shift,  # 2
        flat_96_z_shift,  # 2
    )
    softLinx.soloSoftRun(hso_3)
    plate_id += 1

    # remove empty 50uL tips from deck
    remove_tip_box(
        current_softLinx=softLinx, 
        empty_tip_loc="Position3", 
        poolID=4,
    )

    # different tear down method (place master plate in STACK 2 for safe keeping)
    softLinx.plateCraneReplaceLid(["SoftLinx.PlateCrane.LidNest1"], ["SoftLinx.Solo.Position6"])
    softLinx.plateCraneMovePlate(["SoftLinx.Solo.Position6"], ["SoftLinx.PlateCrane.Stack2"], poolID=2)  # place master plate in different stack to save
    softLinx.plateCraneReplaceLid(["SoftLinx.PlateCrane.LidNest2"], ["SoftLinx.Solo.Position4"])
    softLinx.plateCraneMovePlate(["SoftLinx.Solo.Position4"],["SoftLinx.Liconic.Nest"])  # move to other deck position, now source plate
    softLinx.plateCraneMoveCrane("SoftLinx.PlateCrane.Safe")

    # load the new plate into the incubator
    softLinx.liconicLoadIncubator(loadID=plate_id)
    softLinx.liconicShake(shaker1Speed=30, shakeTime=overnight_incubation_time_2)
    
 
    #* OVERNIGHT PLATE --> TEST PLATE
    # preheat hidex to 37C
    softLinx.hidexRun("SetTemp37")

    # set up the SOLO deck
    set_up(current_softLinx=softLinx, incubator_plate_id=plate_id, empty_tip_deck_loc="Position3")

    # generate and run the liquidhandling hso
    hso_4 = generate_hso(
        overnight_to_test_filename, 
        directory_name,
        overnight_to_test_asp_volume, # 2uL
        default_num_mix,  # 3
        default_mix_volume,  # 45uL 
        default_mix_volume,  # 45uL
        flat_96_z_shift,  # 2
        flat_96_z_shift,  # 2
    )
    softLinx.soloSoftRun(hso_4)
    plate_id += 1
    
    # clear SOLO deck and prepare for T0 Hidex reading
    remove_tip_box(  # remove 50uL tips
        current_softLinx=softLinx,
        empty_tip_loc="Position3", 
        poolID=3,  # pool id = stack num of dest 
    )
    softLinx.plateCraneReplaceLid(["SoftLinx.PlateCrane.LidNest1"], ["SoftLinx.Solo.Position6"])
    softLinx.plateCraneMovePlate(["SoftLinx.Solo.Position6"], ["SoftLinx.PlateCrane.Stack1"], poolID=1)

    #* TEST PLATE HIDEX READINGS 
    # T0 hidex reading
    softLinx.plateCraneMovePlate(["SoftLinx.Solo.Position4"],["SoftLinx.Hidex.Nest"])
    softLinx.plateCraneMoveCrane("SoftLinx.PlateCrane.Safe")
    softLinx.hidexRun(hidex_assay_name)
    softLinx.runProgram(   
        "C:\\Users\\svcaibio\\Dev\\liquidhandling\\zeromq\\utils\\send_data.bat", 
        arguments=f"{plate_id} {directory_name} {data_format}"
    )
    softLinx.plateCraneMovePlate(["SoftLinx.Hidex.Nest"],["SoftLinx.Liconic.Nest"])  #TODO: define Liconic.NestAfterHidex location
    softLinx.hidexClose()
    softLinx.plateCraneReplaceLid(["SoftLinx.PlateCrane.LidNest2"],["SoftLinx.Liconic.Nest"])
    softLinx.plateCraneMoveCrane("SoftLinx.PlateCrane.Safe")
    softLinx.liconicLoadIncubator(loadID=plate_id)
    softLinx.liconicShake(shaker1Speed=30, shakeTime=incubation_time_between_readings)
    
    for i in range(num_readings-1):  
        # take hidex reading
        take_hidex_reading(current_softLinx=softLinx, directory_name=directory_name, incubator_plate_id=plate_id,hidex_assay=hidex_assay_name)

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

    """
    SEND NEW PROTOCOL TO WORK CELL (HUDSON01) ------------------------------------------------------------------
    """
    try:
        # TODO: change to full path on lambda6
        child_message_sender = child_pid = Popen(
            [
                "python",
                "../../zeromq/lambda6_send_instructions.py",
                "-d",
                directory_path,
                "-i", 
                str(num_assay_plates),
                str(num_assay_wells),
                assay_plate_type,
                str(is_test),
            ],
            start_new_session=True,
        ).pid

        print("New instruction directory passed to lambda6_send_message.py")
    except BaseException as e:
        print(e)
        print("Could not send new instructions to hudson01")



# HELPER METHODS: ---------------------------------------------------------------
def set_up(
    current_softLinx:SoftLinx, 
    incubator_plate_id, 
    empty_tip_deck_loc,
    new_tip_storage_loc="SoftLinx.PlateCrane.Stack4",
): 
    """ set_up

        Descrition: Sets up SOLO deck for liquidhandling
                    Retreives specified plate from incubator and places it on SOLO position 6
                    Retreives prefilled LB plate from Stack5 and places it on SOLO position 4

        Parameters: 
            current_softLinx: the instance of SoftLinx that should add the included steps
            incubator_plate_id: plate_id corresponding to incubaotor plate to place on SOLO deck
            empty_tip_deck_loc: TODO
            new_tip_storage_loc: TODO
            
    """
    # place new tip box on the deck
    replace_tip_box(
        current_softLinx=current_softLinx, 
        empty_tip_loc=empty_tip_deck_loc, 
        full_tip_storage=new_tip_storage_loc, 
        poolID=4,  # pool id = stack num
    )  

    # place plate from incubator on deck, remove lid
    current_softLinx.liconicUnloadIncubator(loadID=incubator_plate_id)
    current_softLinx.plateCraneMovePlate(["SoftLinx.Liconic.Nest"],["SoftLinx.Solo.Position6"])  
    current_softLinx.plateCraneRemoveLid(["SoftLinx.Solo.Position6"],["SoftLinx.PlateCrane.LidNest1"])

    # place prefilled media plate onto solo deck position 4, remove lid
    current_softLinx.plateCraneMovePlate(["SoftLinx.PlateCrane.Stack5"],["SoftLinx.Solo.Position4"], poolID=5)  # pool id = stack num
    current_softLinx.plateCraneRemoveLid(["SoftLinx.Solo.Position4"],["SoftLinx.PlateCrane.LidNest2"])

    current_softLinx.plateCraneMoveCrane("SoftLinx.PlateCrane.Safe")


# ---------------------------------------------------------------------------------
def tear_down(
    current_softLinx:SoftLinx, 
    incubator_plate_id, 
    incubation_time, 
    shaker_speed=30, 
    empty_tip_deck_loc="Position3", 
    empty_tip_storage_loc="SoftLinx.PlateCrane.Stack3",
): 
    """ tear_down
    
        Description: Clears the SOLO deck after liquidhandling is complete
                     Transfers the plate into the incubator

        Parameters:
            current_softLinx: the instance of SoftLinx that should add the included steps
            incubator_plate_id: plate_id of the newly completed plate to be placed in incubator
            incubation_time: How long the plate should incubate before next step of the protocol 
                note: must be a list of integers [days, hours, minutes, seconds] (ex. [0,3,0,0] means 3 hours)
            shaker_speed: shaker setting for incubator. Must be 1-50. (20 = 200 rpm, 30 = 300 rpm, etc.)
            empty_tip_deck_loc: TODO 
            empty_tip_storage_loc: TODO
    
    """
    # remove used tip box from deck
    remove_tip_box(
        current_softLinx=current_softLinx, 
        empty_tip_loc=empty_tip_deck_loc, 
        empty_tip_storage=empty_tip_storage_loc, 
        poolID=3, # pool id = stack num
    )  

    # remove used origin plate from deck and place in stack 1
    current_softLinx.plateCraneReplaceLid(["SoftLinx.PlateCrane.LidNest1"], ["SoftLinx.Solo.Position6"])
    current_softLinx.plateCraneMovePlate(["SoftLinx.Solo.Position6"], ["SoftLinx.PlateCrane.Stack1"], poolID=1)

    # replace lid on new plate and move to incubator nest 
    current_softLinx.plateCraneReplaceLid(["SoftLinx.PlateCrane.LidNest2"], ["SoftLinx.Solo.Position4"])
    current_softLinx.plateCraneMovePlate(["SoftLinx.Solo.Position4"],["SoftLinx.Liconic.Nest"])
    current_softLinx.plateCraneMoveCrane("SoftLinx.PlateCrane.Safe")

    # load the new plate into the incubator
    current_softLinx.liconicLoadIncubator(loadID=incubator_plate_id)
    current_softLinx.liconicShake(shaker1Speed=shaker_speed, shakeTime=incubation_time)


# ----------------------------------------------------------------------------------
def take_hidex_reading(current_softLinx:SoftLinx, directory_name, incubator_plate_id, hidex_assay): 
    """ take_hidex_reading

        Description: Removes the specified plate (plate_id) from incubator and transfers to Hidex
                     Runs desired Hidex assay (hidex_assay) to collect data on plate
                     Transfers data file to lambda6 for data processing

        Parameters: 
            current_softLinx: the instance of SoftLinx that should add the included steps
            incubator_plate_id: plate_id of the newly completed plate to be placed in incubator
            hidex_assay: string name of assay protocol name on Hidex app (on hudson01) that you wish to run

    """
    # remove specified plate from incubator
    current_softLinx.liconicUnloadIncubator(loadID=incubator_plate_id)

    # remove lid and transfer to Hidex
    current_softLinx.plateCraneRemoveLid(["SoftLinx.Liconic.Nest"],["SoftLinx.PlateCrane.LidNest2"])
    current_softLinx.plateCraneMovePlate(["SoftLinx.Liconic.Nest"],["SoftLinx.Hidex.Nest"])
    current_softLinx.plateCraneMoveCrane("SoftLinx.PlateCrane.Safe")

    # take Hidex reading 
    current_softLinx.hidexRun(hidex_assay)

    # transfer data to lambda6
    data_format = "dna_assembly"
    current_softLinx.runProgram(   
        "C:\\Users\\svcaibio\\Dev\\liquidhandling\\zeromq\\utils\\send_data.bat", 
        arguments=f"{incubator_plate_id} {directory_name} {data_format}"
    )

# ----------------------------------------------------------------------------------
def generate_hso(
    file_path, 
    directory_name, 
    volume, 
    num_mix, 
    origin_mix_volume, 
    destination_mix_volume, 
    origin_z_shift, 
    destination_z_shift):
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
            "DeepBlock.96.VWR-75870-792.sterile", # Position1
            "Empty",  # Position2
            "TipBox.50uL.Axygen-EV-50-R-S.tealbox",  # Position3
            "Plate.96.Corning-3635.ClearUVAssay",   # Position4
            "Empty", # Position5
            "Plate.96.Corning-3635.ClearUVAssay",  # Position6
            "Empty",  # Position7
            "Empty",  # Position8
        ],
    )
    
    for i in range(1,13):  # for every column in the plate
        soloSoft.getTip("Position3")
        soloSoft.aspirate(
            position="Position6", 
            aspirate_volumes=Plate_96_Corning_3635_ClearUVAssay().setColumn(i, volume),
            aspirate_shift=[0,0,origin_z_shift], 
            mix_at_start=True, 
            mix_cycles=num_mix, 
            mix_volume=origin_mix_volume,
            dispense_height=origin_z_shift,
        )
        soloSoft.dispense(
            position="Position4", 
            dispense_volumes=Plate_96_Corning_3635_ClearUVAssay().setColumn(i, volume),
            dispense_shift=[0,0,destination_z_shift],
            mix_at_finish=True, 
            mix_cycles=num_mix, 
            mix_volume=destination_mix_volume, 
            aspirate_height=destination_z_shift,
        )

        if two_transfers == True: # TODO: Remove this, not necessary anymore
            soloSoft.aspirate(
                position="Position6", 
                aspirate_volumes=Plate_96_Corning_3635_ClearUVAssay().setColumn(i, volume),
                aspirate_shift=[0,0,origin_z_shift], 
                mix_at_start=True, 
                mix_cycles=num_mix, 
                mix_volume=origin_mix_volume,
                dispense_height=origin_z_shift,
            )
            soloSoft.dispense(
                position="Position4", 
                dispense_volumes=Plate_96_Corning_3635_ClearUVAssay().setColumn(i, volume),
                dispense_shift=[0,0,destination_z_shift],
                mix_at_finish=True, 
                mix_cycles=num_mix, 
                mix_volume=destination_mix_volume, 
                aspirate_height=destination_z_shift,
            )

    soloSoft.shuckTip()
    soloSoft.savePipeline()

    hudson01_hso_path = "C:\\labautomation\\instructions\\" + directory_name + "\\" + os.path.basename(file_path)
    print(hudson01_hso_path)

    return hudson01_hso_path 


# -------------------------------------------------------------------------------------------------------------
def generate_glycerol_hso(file_path, directory_name, volume, num_mix, origin_mix_volume, destination_mix_volume, origin_z_shift, destination_z_shift):
    """generate_glycerol_hso

    Description: TODO

    Parameters: TODO

    Returns: TODO

    # TODO: maybe use larger tips to make this faster

    """
    soloSoft = SoloSoft(
        filename=file_path,
        plateList=[
            "DeepBlock.96.VWR-75870-792.sterile",
            "Empty",
            "TipBox.180uL.Axygen-EVF-180-R-S.bluebox", 
            "Plate.96.Corning-3635.ClearUVAssay",
            "Empty",
            "Plate.96.Corning-3635.ClearUVAssay",
            "Empty",
            "Empty",
        ],
    )

    for i in range(1,13):  # for each column in the whole plate
        soloSoft.getTip("Position3")
        soloSoft.aspirate(
            position="Position1", # glycerol stock 96 deep well
            aspirate_volumes=Reservoir_12col_Agilent_201256_100_BATSgroup().setColumn(1, volume),
            aspirate_shift=[0,0,origin_z_shift], 
            mix_at_start=True, 
            mix_cycles=num_mix, 
            mix_volume=origin_mix_volume,
            dispense_height=origin_z_shift,
            syringe_speed=75,
        )
        soloSoft.dispense(
            position="Position6", # master plate
            dispense_volumes=Plate_96_Corning_3635_ClearUVAssay().setColumn(i, volume),
            dispense_shift=[0,0,destination_z_shift],
            mix_at_finish=True, 
            mix_cycles=num_mix, 
            mix_volume=destination_mix_volume, 
            aspirate_height=destination_z_shift,
            syringe_speed=75,
        )

    soloSoft.shuckTip()
    soloSoft.savePipeline()

    hudson01_hso_path = "C:\\labautomation\\instructions\\" + directory_name + "\\" + os.path.basename(file_path)
    print(hudson01_hso_path)

    return hudson01_hso_path 


# ----------------------------------------------------------------------------------
def main(args):
    # handle command line args
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-t", 
        "--is_test",
        help="use -t or --is_test only if the run is a test and the data can be deleted",  
        action="store_true",
    )
    args = vars(parser.parse_args())

    # pass to method
    generate_post_transformation(args["is_test"])


# ----------------------------------------------------------------------------------
if __name__ == "__main__":
    # execute only if run as a script
    main(sys.argv)
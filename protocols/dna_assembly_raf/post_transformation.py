import os
from re import L
import time
from liquidhandling import SoftLinx
from .utils.tip_utils import replace_tip_box, remove_tip_box
from .utils.send_protocol import send_protocol
from .utils.wc_setup import set_up
from .utils.wc_tear import tear_down
from .utils.hydex import take_hidex_reading

from .generate_deletion_hso import generate_hso
from .generate_glycerol_hso import generate_glycerol_hso
 

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
    default_incubation_time = [0,8,0,0]  # --> 0 days, 3 hours, 0 minutes, 0 seconds 
    overnight_incubation_time_1= [0,19,0,0]  # --> 0 days, 8 hours, 0 minutes, 0 seconds
    overnight_incubation_time_2= [0,20,0,0]  # --> 0 days, 8 hours, 0 minutes, 0 seconds
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

    i_list =[ 
        str(num_assay_plates),
        str(num_assay_wells),
        assay_plate_type,
        str(is_test),
        ]

    send_protocol(directory_path,i_list)




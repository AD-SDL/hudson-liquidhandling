import argparse
from multiprocessing import pool
import os
import sys
import time
from subprocess import Popen
from liquidhandling import SoloSoft
from liquidhandling import SoftLinx
from liquidhandling import DeepBlock_96VWR_75870_792_sterile
from liquidhandling import Reservoir_12col_Agilent_201256_100_BATSgroup
from liquidhandling import Plate_96_Corning_3635_ClearUVAssay
from tip_utils import replace_tip_box, remove_tip_box
from functions import *


"""
Version to plate multiple treatments within the same 384 well plate (one per 6 column quadrant)
"""


def generate_SD_384_repeatable(
    treatment, # string list of treatment names
    predicted_IC50=None,  # TODO: handle predicted IC50
    culture_column=None,  # int list of cell culture columns
    culture_dil_column=None, # int list of dilution columns for 1:10 culture dilutions
    media_start_column=None,  # int list of columns to draw media from (requires 2 columns, 1 means columns 1 and 2)
    treatment_dil_half=None,  # int list of which half of treatment dilution plate to use
    is_test=False,
):

    return_val = "PASS"

    # TODO: add constraints to user input?
    # check that all user inputs are lists
    if not isinstance(treatment, list) or not isinstance(culture_column, list) or not isinstance(culture_dil_column, list) or not isinstance(treatment_dil_half, list):
        raise TypeError (
            "all command line arguments must be lists of equal length. -tr is a list of strings while all other arguments are lists of integers"
        )
    else: # check that all user inputs are lists of equal length
        all_equal_lengths = True
        for each in [len(culture_column), len(culture_dil_column), len(media_start_column), len(treatment_dil_half)]:
            if not each == len(treatment):
                all_equal_lengths == False
        if not all_equal_lengths:
            raise ValueError (
                "all command line arguments must be lists of equal length"
            )

    # * Program variables
    blowoff_volume = 10
    num_mixes = 3
    media_z_shift = 0.5
    reservoir_z_shift = 0.5  # z shift for deep blocks (Deck Positions 3 and 5)
    flat_bottom_z_shift = 2  # Note: 1 is not high enough (tested)
    lambda6_path = "/lambda_stor/data/hudson/instructions/" # location where instructions are sent to on lambda6
    # lambda6_path = "C:\\Users\\svcaibio\\Dev\\liquidhandling\\protocols\\SerialDilution384\\test_hso\\" # TODO change directory name

    # Step 1 variables
    media_transfer_volume_s1 = 20 # volume of media dispensed into assay plate well
    culture_transfer_volume_s1 = 10 # volume of diluted cells dispensed into assay platee well 1:3 ratio culture to media volume
    half_dilution_media_volume = 99 # half of volume of media dispensed into culture dilution column
    dilution_culture_volume = 22 # half of volume of culture cells dispensed into culture dilution column
    culture_plate_mix_volume_s1 = 100  # mixing volume used when cells are added to dilution plate
    culture_plate_num_mix = 7 # number of times cells are mixed before being added to dilution plate
    culture_dilution_num_mix = 10 # number of times cells are mixed after being added to dilution plate
    growth_plate_mix_volume_s1 = 20 # mixing volume after cells are dispensed into assay plate
    culture_dilution_mix_volume = 180 # mixing volume when performing large final mix in cell dilution plate

    # Step 2 variables
    media_transfer_volume_s2 = (
        120  # half of volume of media dispensed into each well of serial dilution plate for prep # two times = 240 uL (will add 240 ul stock for 1:2 dilution)
    )
    last_column_transfer_volume_s2 = (
        120  # half of volume of media dispensed into last column of serial dilution plate for prep # two times = 240uL (to equal volume in 1:10 dilution wells)
    )
    serial_antibiotic_transfer_volume_s2 = 120  # half of volume of treatment dispensed into first column of serial dilution half # transfers twice (240tr + 240 lb = 1:2 dil)
    serial_source_mixing_volume_s2 = 110 # mixing volume in treatment source before aspirating for serial dilution plate
    serial_source_num_mixes_s2 = 5 # number of mixes performed in treatment source before aspirating for serial dilution plate
    serial_destination_mixing_volume_s2 = 150 # mixing volume used when serial dilution being performed between columns of serial dilution plate

    # Step 3 variables
    antibiotic_transfer_volume_s3 = 30 # volume of treatment from serial dilution dispensed into assay plate # reduced to be 1:1 with media + cells
    antibiotic_mix_volume_s3 = 30 # mixing volume used in serial dilution plate before aspirating treatment for assay plate
    destination_mix_volume_s3 = 50 # mixing volume used in assay plate after treatment has been dispensed in assay plate

    # * Create folder to store all instruction files
    project = "SerialDil384"
    project_desc = "loop"
    version_num = "384"
    timestamp = str(time.time()).split(".")[0]
    directory_name = f"{project}-{project_desc}-{version_num}-{timestamp}"
    directory_path = os.path.join(
        os.path.realpath(os.path.dirname(lambda6_path)), directory_name
    )

    # populate info list
    num_assay_plates = len(culture_column) # from cl args
    num_assay_wells = 384  # hardcoded for now
    assay_plate_type = "hidex"
    #info_str = f"{num_assay_plates} {num_assay_wells} {assay_plate_type} {directory_name}"
    #print(info_str)

    # * create new directory to hold new instructions
    try:
        os.makedirs(directory_path, exist_ok=True)
        print(f"Protocol directory created: {directory_path}")
    except OSError as e:
        print(e)
        print(f"failed to create new directory for instructions: {directory_path}")

    # * Lists for every generated hso file
    # TODO: should be able to keep the same? but look into it
    media_to_assay_hso = []
    media_to_culture_hso = []
    cells_to_assay_hso = []
    serial_dilution_hso = []
    treatment_to_assay_hso = []

    #* LOOP: produce 5 separate .hso files per treatment
    for k in range(len(treatment)):
        # * Get location of treatment
        try:
            treatment_plate_loc, treatment_column = find_treatment_loc(treatment[k])
        except Error as e:
            print(f"Unable to locate treatment {treatment[k]}")
            raise  # need to know locaton of treatment, rest of protocol useless if not specified
        # TODO, check to see if using full plate? or fill plate with media regardless?
        # TODO, might need separte file of functions
        #TODO: run one quarter at a time? or fill entire plate at once?

        # establish start and end columns for current quadrant:
        if k%4 == 0:
            start_col = 1
            end_col = 6
        else:
            end_col = ((k%4) * 6) + 6
            start_col = end_col - 5

        #* completes protocol for one single quadrant only


        #* generate media transfer to assay hso # one col of tips
        media_to_assay_hso.append(generate_media_transfer_to_quarter_assay_hso(directory_path=directory_path,
        filename="media_to_assay_quarter_1.hso",
        media_start_column=media_start_column, 
        media_z_shift=media_z_shift,
        media_transfer_volume_s1=media_transfer_volume_s1,
        flat_bottom_z_shift=flat_bottom_z_shift,
        start_col=start_col,
        end_col=end_col,
        k=k))

        
        #* fill cell dilution and treatment dilution plates with media # one col of tips 
        media_to_culture_hso.append(generate_fill_culture_dilution_and_treatment_plates_with_media_hso(directory_path=directory_path,
        filename="media_to_culture.hso",
        media_start_column=media_start_column,
        media_z_shift=media_z_shift,
        flat_bottom_z_shift=flat_bottom_z_shift,
        reservoir_z_shift=reservoir_z_shift,
        half_dilution_media_volume=half_dilution_media_volume,
        dilution_culture_volume=dilution_culture_volume,
        culture_plate_num_mix=culture_plate_num_mix,
        culture_plate_mix_volume_s1=culture_plate_mix_volume_s1,
        culture_dil_column=culture_dil_column,
        k=k,
        culture_column=culture_column,
        num_mixes=num_mixes,
        culture_dilution_num_mix=culture_dilution_num_mix,
        culture_dilution_mix_volume=culture_dilution_mix_volume,
        blowoff_volume=blowoff_volume))

        #* add diluted cells to assay # one column of tips
        cells_to_assay_hso.append(generate_add_diluted_cells_to_assay_loop_hso(directory_path=directory_path,
        filename="cells_to_assay.hso",
        media_start_column=media_start_column,
        media_z_shift=media_z_shift,
        flat_bottom_z_shift=flat_bottom_z_shift,
        reservoir_z_shift=reservoir_z_shift,
        culture_transfer_volume_s1=culture_transfer_volume_s1,
        culture_dil_column=culture_dil_column,
        num_mixes=num_mixes,
        growth_plate_mix_volume_s1=growth_plate_mix_volume_s1,
        start_col=start_col,
        end_col=end_col,
        k=k))


        #* perform serial dilution of given treatment # two columns of tips
        serial_dilution_hso.append(generate_serial_dlution_treatment_hso(directory_path=directory_path,
        filename="treatment_serial_dilution.hso",
        treatment_dil_half=treatment_dil_half,
        media_start_column=media_start_column,
        media_transfer_volume_s2=media_transfer_volume_s2,
        media_z_shift=media_z_shift,
        reservoir_z_shift=reservoir_z_shift,
        last_column_transfer_volume_s2=last_column_transfer_volume_s2,
        treatment_plate_loc=treatment_plate_loc,
        serial_antibiotic_transfer_volume_s2=serial_antibiotic_transfer_volume_s2,
        treatment_column=treatment_column,
        blowoff_volume=blowoff_volume,
        serial_source_num_mixes_s2=serial_source_num_mixes_s2,
        serial_source_mixing_volume_s2=serial_source_mixing_volume_s2,
        serial_destination_mixing_volume_s2=serial_destination_mixing_volume_s2,
        k=k,
        num_mixes=num_mixes
        ))

        #* add antibiotic to assay # one column of tips
        treatment_to_assay_hso.append(generate_add_antibioitc_to_assay_hso(directory_path=directory_path,
        filename="treatment_to_assay.hso",
        treatment_dil_half=treatment_dil_half,
        antibiotic_transfer_volume_s3=antibiotic_transfer_volume_s3,
        num_mixes=num_mixes,
        antibiotic_mix_volume_s3=antibiotic_mix_volume_s3,
        reservoir_z_shift=reservoir_z_shift,
        destination_mix_volume_s3=destination_mix_volume_s3,
        flat_bottom_z_shift=flat_bottom_z_shift,
        start_col=start_col,
        end_col=end_col,
        k=k,))

        # TODO: tip total per treatment: 5, can use 2 boxes per treatment as of now
    
    # * ADD TO SOFTLINX PIPELINE

    # initialize softLinx
    softLinx = SoftLinx("Steps_384_assay_multi_treatment", os.path.join(directory_path, "steps384_assay_multi_treatment.slvp"))

    # softLinx.setPlates(
    #     {"SoftLinx.PlateCrane.Stack5": "Corning 3540", }
    # )

    # declare 384 well plates in stack 5 and tip boxes in stack 4
    softLinx.setPlates(
        {"SoftLinx.PlateCrane.Stack5": "Plate.96.Corning-3635.ClearUVAssay", "SoftLinx.PlateCrane.Stack4": "TipBox.180uL.Axygen-EVF-180-R-S.bluebox"}
    )

    # set up equiptment
    softLinx.hidexRun("SetTemp37")
    softLinx.liconicBeginShake(shaker1Speed=30)

    #* loop over treatments, every four treatments, swap out assay plate from stack 5 to position 4

    plate_num = 1 # keeps track of how many plates we have created

    for k in range(len(treatment)):

        #* if first treatment, get fresh assay plate from stack 5, move to position 4, and new tip box from stack 4, move to position 3
        if k == 0:
            softLinx.plateCraneMovePlate(
            ["SoftLinx.PlateCrane.Stack5"], ["SoftLinx.Solo.Position4"], hasLid=True, poolID=5
        )
        # remove lid and place in Lid Nest
            softLinx.plateCraneRemoveLid(
            ["SoftLinx.Solo.Position4"], ["SoftLinx.PlateCrane.LidNest2"]
        )
            replace_tip_box(softLinx, "Position3")
            softLinx.soloSoftResetTipCount(3)

        #* replace tip box and swap out treatment dilution plate every two treatments
        #TODO: figure out effective way to swap serial dilution plate, or see if there's a manual pause to do manually
        elif k % 2 == 0:
            remove_tip_box(softLinx, "Position3")
            replace_tip_box(softLinx, "Position3")
            softLinx.soloSoftResetTipCount(3)

            # TODO: treatment plate 
            #* for now, have to manually swap serial dilution dilution plate with empty every 2 treatments
        
        softLinx.plateCraneMoveCrane("SoftLinx.PlateCrane.Safe")
        



        #* run all liquid handling steps for current treatment
        softLinx.soloSoftRun(
            "C:\\labautomation\\instructions\\"
            + directory_name
            + "\\"
            + f"plate{k}_"
            + os.path.basename(media_to_assay_hso[k])
        )

        softLinx.soloSoftRun(
            # "C:\\Users\\svcaibio\\Dev\\liquidhandling\\protocols\\campaign2\\test_hso\\"
            "C:\\labautomation\\instructions\\"
            + directory_name
            + "\\"
            + f"plate{k}_"
            + os.path.basename(media_to_culture_hso[k])
        )

        softLinx.soloSoftRun(
            "C:\\labautomation\\instructions\\"
            + directory_name
            + "\\"
            + f"plate{k}_"
            + os.path.basename(cells_to_assay_hso[k])
        )

        softLinx.soloSoftRun(
            "C:\\labautomation\\instructions\\"
            + directory_name
            + "\\"
            + f"plate{k}_"
            + os.path.basename(serial_dilution_hso[k])
        )

        softLinx.soloSoftRun(
            "C:\\labautomation\\instructions\\"
            + directory_name
            + "\\"
            + f"plate{k}_"
            + os.path.basename(treatment_to_assay_hso[k])
        )

      

        #* if fourth or last treatment total, move assay plate from position 4 to hidex, run protocol, replace lid, load incubator, move to safe
        if k == len(treatment) - 1: # last treatment
            softLinx.plateCraneMovePlate(["SoftLinx.Solo.Position4"], ["SoftLinx.Hidex.Nest"])
            softLinx.hidexClose()
            softLinx.plateCraneMoveCrane("SoftLinx.PlateCrane.Safe")
            softLinx.hidexRun("Campaign1_noIncubate2_384")

            softLinx.runProgram(
            "C:\\Users\\svcaibio\\Dev\\liquidhandling\\zeromq\\utils\\send_data.bat", arguments=f"{k} {directory_name} serial_dilution"
            )

            # Move plate back to incubator, replace lid
            softLinx.plateCraneMovePlate(["SoftLinx.Hidex.Nest"], ["SoftLinx.Liconic.Nest"])
            softLinx.hidexClose()
            softLinx.plateCraneReplaceLid(["SoftLinx.PlateCrane.LidNest2"], ["SoftLinx.Liconic.Nest"])
            softLinx.plateCraneMoveCrane("SoftLinx.PlateCrane.Safe")
            softLinx.liconicLoadIncubator(loadID=plate_num, holdWithoutIncubationTime=True)

            softLinx.liconicShake(shaker1Speed=30, shakeTime=[0,1,0,0]) # 1 hour
        elif k != 0:
            if (k+1) % 4 == 0: # not the first treatment, but last treatment of plate
                softLinx.plateCraneMovePlate(["SoftLinx.Solo.Position4"], ["SoftLinx.Hidex.Nest"])
                softLinx.hidexClose()
                softLinx.plateCraneMoveCrane("SoftLinx.PlateCrane.Safe")
                softLinx.hidexRun("Campaign1_noIncubate2_384")

                # lambda6 TODO
                softLinx.runProgram(
                "C:\\Users\\svcaibio\\Dev\\liquidhandling\\zeromq\\utils\\send_data.bat", arguments=f"{k} {directory_name} serial_dilution"
                )

                # Move plate back to incubator, replace lid
                softLinx.plateCraneMovePlate(["SoftLinx.Hidex.Nest"], ["SoftLinx.Liconic.Nest"])
                softLinx.hidexClose()
                softLinx.plateCraneReplaceLid(["SoftLinx.PlateCrane.LidNest2"], ["SoftLinx.Liconic.Nest"])
                softLinx.plateCraneMoveCrane("SoftLinx.PlateCrane.Safe")
                softLinx.liconicLoadIncubator(loadID=plate_num, holdWithoutIncubationTime=True)

                # add one ot plate num, still more plates
                plate_num+=1

                # replenish assay plate
                softLinx.plateCraneMovePlate(
                ["SoftLinx.PlateCrane.Stack5"], ["SoftLinx.Solo.Position4"], hasLid=True, poolID=5
            )
        
            elif k == len(treatment) - 1: # last treatment
                softLinx.plateCraneMovePlate(["SoftLinx.Solo.Position4"], ["SoftLinx.Hidex.Nest"])
                softLinx.hidexClose()
                softLinx.plateCraneMoveCrane("SoftLinx.PlateCrane.Safe")
                softLinx.hidexRun("Campaign1_noIncubate2_384")

                # lambda6 TODO
                softLinx.runProgram(
                "C:\\Users\\svcaibio\\Dev\\liquidhandling\\zeromq\\utils\\send_data.bat", arguments=f"{k} {directory_name} serial_dilution"
                )

                # Move plate back to incubator, replace lid
                softLinx.plateCraneMovePlate(["SoftLinx.Hidex.Nest"], ["SoftLinx.Liconic.Nest"])
                softLinx.hidexClose()
                softLinx.plateCraneReplaceLid(["SoftLinx.PlateCrane.LidNest2"], ["SoftLinx.Liconic.Nest"])
                softLinx.plateCraneMoveCrane("SoftLinx.PlateCrane.Safe")
                softLinx.liconicLoadIncubator(loadID=plate_num, holdWithoutIncubationTime=True)

                # add one ot plate num
                plate_num+=1

                softLinx.liconicShake(shaker1Speed=30, shakeTime=[0,1,0,0]) # 1 hour




        
        # else continue on to next treatment 
            
    # TODO: check out softlinx parallel capabilities
    #* wait an hour *** less: figure out time between plates *** place all plates into hidex again

    for i in range(12): # 12 hourly scans
        for k in range(plate_num): # plate_num = total number of assay plates
            softLinx.liconicUnloadIncubator(loadID=k+1)
            softLinx.plateCraneRemoveLid(["SoftLinx.Liconic.Nest"], ["SoftLinx.PlateCrane.LidNest2"])
            softLinx.plateCraneMovePlate(["SoftLinx.Liconic.Nest"], ["SoftLinx.Hidex.Nest"])
            softLinx.hidexClose()
            softLinx.plateCraneMoveCrane("SoftLinx.PlateCrane.Safe")
            softLinx.hidexRun("Campaign1_noIncubate2_384")

            # lambda6
            softLinx.runProgram(
            "C:\\Users\\svcaibio\\Dev\\liquidhandling\\zeromq\\utils\\send_data.bat", arguments=f"{k} {directory_name} serial_dilution"
        )

            softLinx.plateCraneMovePlate(["SoftLinx.Hidex.Nest"], ["SoftLinx.Liconic.Nest"])
            softLinx.hidexClose()
            softLinx.plateCraneReplaceLid(["SoftLinx.PlateCrane.LidNest2"], ["SoftLinx.Liconic.Nest"])
            softLinx.plateCraneMoveCrane("SoftLinx.PlateCrane.Safe")
            softLinx.liconicLoadIncubator(loadID=k+1, holdWithoutIncubationTime=True)
    

        
        softLinx.liconicShake(shaker1Speed=30, shakeTime=[0,1,0,0]) # 1 hour


    #* END LOOP

    softLinx.hidexRun("SetTemp20")
    softLinx.liconicEndShake()
    
    #* disposes of all plates into stack 2
    for k in range(plate_num):
        softLinx.liconicUnloadIncubator(loadID=k+1)
        softLinx.plateCraneMovePlate(["SoftLinx.Liconic.Nest"], ["SoftLinx.PlateCrane.Stack2"],poolID = 2)
    softLinx.plateCraneMoveCrane("SoftLinx.PlateCrane.Safe")
    # save protocol to write instructions to .slvp file, create .txt manifest, and .ahk remote start file
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

def find_treatment_loc(treatment_name):  # TODO: Move this method out of protocol file
    """
    Connect to SQL database. Determine plate # and well location of desired treatment
    (for now, these locations will be hardcoded (plate assumed to be on Solo deck))
    """
    treatment_locations = {
        "col1": ["Position8", 1],
        "col2": ["Position8", 2],
        "col3": ["Position8", 3],
        "col4": ["Position8", 4],
        "col5": ["Position8", 5],
        "col6": ["Position8", 6],
        "col7": ["Position8", 7],
        "col8": ["Position8", 8],
        "col9": ["Position8", 9],
        "col10": ["Position8", 10],
        "col11": ["Position8", 11],
        "col12": ["Position8", 12],
    }

    return treatment_locations[treatment_name]


def main(args):
    # Parse args
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-tr",
        "--treatment",
        nargs="*",
        help="treatment to apply to cells",
        required=True,
        type=str,
    )
    parser.add_argument(
        "-IC50",
        "--predicted_IC50",
        help="predicted_IC50, must be a float (do not include units)",
        required=False,
        type=float,
        nargs="*",
    )
    parser.add_argument(
        "-cc",
        "--culture_column",
        help="culture plate column to use, must be an integer (ex. 3 means column 3)",
        required=False,
        type=int,
        nargs="*",
    )
    parser.add_argument(
        "-mc",
        "--media_start_column",
        help="media plate column to start with, must be an integer (ex. 1) Will use column specified(i) and column(i+1). (ex. -mc 1 = first and second column)",
        required=False,
        type=int,
        nargs="*",
    )
    parser.add_argument(
        "-tdh",
        "--treatment_dilution_half",
        help="which half of the treatment serial dilution plate to use, must be an integer (1 or 2). 1 = columns 1-6, 2 = columns 7-12",
        required=False,
        type=int,
        nargs="*",
    )
    parser.add_argument(
        "-cdc",
        "--culture_dilution_column",
        help="column of 10-fold culture dilution plate to use, must be an integer (ex. 1 means column 1)",
        required=False,
        type = int,
        nargs="*",
    )
    parser.add_argument(
        "-t",
        "--is_test",
        help="use -t or --is_test only if the run is a test and the data can be deleted",
        action="store_true",
    )
    args = vars(parser.parse_args())
    print(
        "treatment(s) = {}, IC50 = {}, culture_column(s) = {}, culture dilution column(s) = {}, media start column(s) = {}, treatment dilution column(s)= {}, is test = {}".format(
            args["treatment"],
            args["predicted_IC50"],
            args["culture_column"],
            args["culture_dilution_column"],
            args["media_start_column"],
            args["treatment_dilution_half"],
            args["is_test"],
        )
    )

    # pass to method
    generate_SD_384_repeatable(
        args["treatment"],
        args["predicted_IC50"],
        args["culture_column"],
        args["culture_dilution_column"],
        args["media_start_column"],
        args["treatment_dilution_half"],
        args["is_test"],
    )


if __name__ == "__main__":
    # execute only if run as a script
    main(sys.argv)


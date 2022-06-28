# TO DO
# variables, plates list, quadrants
# divide hso steps
import argparse
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
from campaign2_loop_dil2x_tiprep_384well_plate_hso_functions import *

"""
Campaign 2 Protocol - 2x dilutions
(7 strains x 1 treatment x 5 dilutions x 2 replicates)
created 06/21/22
SOLO DECK ARRANGEMENT:
Pos 1 = 96 deep well media reservoir
Pos 2 = EMPTY (heat nest)
Pos 3 = 180uL tips (filtered if possible)
Pos 4 = EMPTY TO START
Pos 5 = 96 deep well culture stock plate
Pos 6 = 96 deep well (empty at start)
Pos 7 = 96 deep well culture dilution plate (plate is empty at start)
Pos 8 = 96 well flat bottom treatment plate (one treatment per column, min 280uL treatment per well)
Stack 5 - 384 well clear, flat-bottom plate w/ lid.  (will be placed on deck pos 4 at start of protocol)
Stack 4 - Full Tip Box Replacements
Stack 3 - Empty Tip Box Storage (empty at start)
Example command line usage: (creating 3 plates)
python campaign2_loop_dil2x.py -tr col1 col2 col3 -cc 1 2 3 -mc 1 3 5 -tdh 1 2 1 -cdc 1 2 3
COMMAND LINE ARGUMENTS:
TODO
"""


def generate_campaign1_repeatable(
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
    # lambda6_path = "/lambda_stor/data/hudson/instructions/"
    lambda6_path = "C:\\Users\\svcaibio\\Dev\\liquidhandling\\protocols\\campaign2\\test_hso\\"

    # Step 1 variables
    media_transfer_volume_s1 = 20 
    culture_transfer_volume_s1 = 10 # reducing volumes, keeping 1:3 ratio culture to media volume
    half_dilution_media_volume = 99
    dilution_culture_volume = 22
    culture_plate_mix_volume_s1 = 100  # mix volume increased for test 09/07/21
    culture_plate_num_mix = 7
    culture_dilution_num_mix = 10
    growth_plate_mix_volume_s1 = 40
    culture_dilution_mix_volume = 180

    # Step 2 variables
    media_transfer_volume_s2 = (
        120  # two times = 240 uL (will add 240 ul stock for 1:2 dilution)
    )
    last_column_transfer_volume_s2 = (
        120  # two times = 240uL (to equal volume in 1:10 dilution wells)
    )
    serial_antibiotic_transfer_volume_s2 = 120  # transfers twice (240tr + 240 lb = 1:2 dil)
    serial_source_mixing_volume_s2 = 110
    serial_source_num_mixes_s2 = 5
    serial_destination_mixing_volume_s2 = 150

    # Step 3 variables
    antibiotic_transfer_volume_s3 = 30 # reduced to be 1:1 with media + cells
    antibiotic_mix_volume_s3 = 90
    destination_mix_volume_s3 = 100

    # * Create folder to store all instruction files
    project = "Campaign2"
    project_desc = "loop"
    version_num = "v1"
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
    media_to_assay_1_hso = []
    media_to_assay_2_hso = []
    media_to_culture_hso = []
    cells_to_assay_1_hso = []
    cells_to_assay_2_hso = []
    serial_dilution_hso = []
    treatment_to_assay_1_hso = []
    treatment_to_assay_2_hso = []

    #* LOOP: produce 8 separate .hso files per plate
    for k in range(len(treatment)):
        # * Get location of treatment
        try:
            treatment_plate_loc, treatment_column = find_treatment_loc(treatment[k])
        except Error as e:
            print(f"Unable to locate treatment {treatment[k]}")
            raise  # need to know locaton of treatment, rest of protocol useless if not specified



        ''' CALL generate_media_transfer_to_assay_hso TWICE, ONE FOR EACH HALF OF PLATE, change start and end cols'''
        media_to_assay_1_hso.append(generate_media_transfer_to_half_assay_hso(directory_path=directory_path,
        filename="media_to_assay_first_half.hso",
media_start_column=media_start_column,
media_z_shift=media_z_shift, 
media_transfer_volume_s1=media_transfer_volume_s1,
flat_bottom_z_shift=flat_bottom_z_shift,
start_col = 1,
end_col = 6,
k=k))

        media_to_assay_2_hso.append(generate_media_transfer_to_half_assay_hso(directory_path=directory_path,
        filename="media_to_assay_second_half.hso",
media_start_column=media_start_column,
media_z_shift=media_z_shift, 
media_transfer_volume_s1=media_transfer_volume_s1,
flat_bottom_z_shift=flat_bottom_z_shift,
start_col = 7,
end_col = 12,
k=k))


        ''' call generate_fill_culture_dilution_and_treatment_plates_with_media_hso'''

        media_to_culture_hso.append(generate_fill_culture_dilution_and_treatment_plates_with_media_hso(directory_path=directory_path,
        filename="culture_dilution.hso",
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
culture_dilution_mix_volume=culture_dilution_mix_volume))

        '''call generate_add_diluted_cells_to_assay_hso twice, once for each half, change start and end cols'''
        cells_to_assay_1_hso.append(generate_add_diluted_cells_to_assay_hso(directory_path=directory_path,
        filename="cells_to_assay_first_half.hso",
media_start_column=media_start_column,
media_z_shift=media_z_shift,
flat_bottom_z_shift=flat_bottom_z_shift,
reservoir_z_shift=reservoir_z_shift,
culture_transfer_volume_s1=culture_transfer_volume_s1,
culture_dil_column=culture_dil_column,
num_mixes=num_mixes,
growth_plate_mix_volume_s1=growth_plate_mix_volume_s1,
start_col=1,
end_col=6,
k=k))

        cells_to_assay_2_hso.append(generate_add_diluted_cells_to_assay_hso(directory_path=directory_path,
        filename="cells_to_assay_second_half.hso",
media_start_column=media_start_column,
media_z_shift=media_z_shift,
flat_bottom_z_shift=flat_bottom_z_shift,
reservoir_z_shift=reservoir_z_shift,
culture_transfer_volume_s1=culture_transfer_volume_s1,
culture_dil_column=culture_dil_column,
num_mixes=num_mixes,
growth_plate_mix_volume_s1=growth_plate_mix_volume_s1,
start_col=7,
end_col=12,
k=k))
        ''' call generate_serial_dlution_treatment_hso'''

        serial_dilution_hso.append(generate_serial_dlution_treatment_hso(directory_path=directory_path,
        filename="serial_dilution_treatment.hso",
treatment_dil_half=treatment_dil_half,
media_start_column=media_start_column,
media_transfer_volume_s2=media_transfer_volume_s2,
media_z_shift=media_z_shift,
reservoir_z_shift=reservoir_z_shift,
last_column_transfer_volume_s2=last_column_transfer_volume_s2,
treatment_plate_loc=treatment,
serial_antibiotic_transfer_volume_s2=serial_antibiotic_transfer_volume_s2,
treatment_column=treatment_column,
blowoff_volume=blowoff_volume,
serial_source_num_mixes_s2=serial_source_num_mixes_s2,
serial_source_mixing_volume_s2=serial_source_mixing_volume_s2,
serial_destination_mixing_volume_s2=serial_destination_mixing_volume_s2,
k=k,
num_mixes=num_mixes))

        

        '''call generate_add_antibioitc_to_assay_hso TWICE, for each half, different start_col, end_col'''
        
        treatment_to_assay_1_hso.append(generate_add_antibioitc_to_assay_first_half_hso(directory_path=directory_path,
        filename="antibiotic_to_assay_first_half.hso",
treatment_dil_half=treatment_dil_half,
antibiotic_transfer_volume_s3=antibiotic_transfer_volume_s3,
num_mixes=num_mixes,
antibiotic_mix_volume_s3=antibiotic_mix_volume_s3,
resevoir_z_shift=reservoir_z_shift,
destination_mix_volume_s3=destination_mix_volume_s3,
flat_bottom_z_shift=flat_bottom_z_shift,
start_col=1,
end_col=6,
k=k,
reservoir_z_shift=reservoir_z_shift))

        treatment_to_assay_2_hso.append(generate_add_antibioitc_to_assay_second_half_hso(directory_path=directory_path,
        filename="antibiotic_to_assay_second_half.hso",
treatment_dil_half=treatment_dil_half,
antibiotic_transfer_volume_s3=antibiotic_transfer_volume_s3,
num_mixes=num_mixes,
antibiotic_mix_volume_s3=antibiotic_mix_volume_s3,
resevoir_z_shift=reservoir_z_shift,
destination_mix_volume_s3=destination_mix_volume_s3,
flat_bottom_z_shift=flat_bottom_z_shift,
start_col=7,
end_col=12,
k=k,
reservoir_z_shift=reservoir_z_shift))

# """
#     ADD ALL STEPS TO SOFTLINX PROTOCOL AND SEND TO HUDSON01 -----------------------------------------------------------------------
# """

 # initialize softLinx
    softLinx = SoftLinx("Steps_384_assay_1_2_3", os.path.join(directory_path, "steps384_assay_1_2_3.slvp"))

    softLinx.setPlates(
        {"SoftLinx.PlateCrane.Stack5": "Corning 3540"}
    )

# set up equiptment
    softLinx.hidexRun("SetTemp37")
    softLinx.liconicBeginShake(shaker1Speed=30)

    #* LOOP: create plates, take t0 reading, transfer to incubator
    for k in range(len(treatment)):
        # restock growth assay plate before run
        softLinx.plateCraneMovePlate(
            ["SoftLinx.PlateCrane.Stack5"], ["SoftLinx.Solo.Position4"], hasLid=True
        )
        # remove lid and place in Lid Nest
        softLinx.plateCraneRemoveLid(
            ["SoftLinx.Solo.Position4"], ["SoftLinx.PlateCrane.LidNest2"]
        )
        

        # current protocol uses 10 columns of tips per plate
        # replace tip box for every treatment unless on first round
        if k == 0:
            replace_tip_box(softLinx, "Protocol3")
            softLinx.soloSoftResetTipCount(3)
        else:
            remove_tip_box(softLinx, "Position3")
            replace_tip_box(softLinx, "Protocol3")
            softLinx.soloSoftResetTipCount(3)

        softLinx.plateCraneMoveCrane("SoftLinx.PlateCrane.Safe")

        # run all liquid handling steps
        softLinx.soloSoftRun(
            "C:\\Users\\svcaibio\\Dev\\liquidhandling\\protocols\\campaign2\\test_hso\\"
            + directory_name
            + "\\"
            + os.path.basename(media_to_assay_1_hso[k])
        )
        softLinx.soloSoftRun(
            "C:\\Users\\svcaibio\\Dev\\liquidhandling\\protocols\\campaign2\\test_hso\\"
            + directory_name
            + "\\"
            + os.path.basename(media_to_assay_2_hso[k])
        )
        softLinx.soloSoftRun(
            "C:\\Users\\svcaibio\\Dev\\liquidhandling\\protocols\\campaign2\\test_hso\\"
            + directory_name
            + "\\"
            + os.path.basename(media_to_culture_hso[k])
        )

        softLinx.soloSoftRun(
            "C:\\Users\\svcaibio\\Dev\\liquidhandling\\protocols\\campaign2\\test_hso\\"
            + directory_name
            + "\\"
            + os.path.basename(cells_to_assay_1_hso[k])
        )
        softLinx.soloSoftRun(
            "C:\\Users\\svcaibio\\Dev\\liquidhandling\\protocols\\campaign2\\test_hso\\"
            + directory_name
            + "\\"
            + os.path.basename(cells_to_assay_2_hso[k])
        )
        softLinx.soloSoftRun(
            "C:\\Users\\svcaibio\\Dev\\liquidhandling\\protocols\\campaign2\\test_hso\\"
            + directory_name
            + "\\"
            + os.path.basename(serial_dilution_hso[k])
        )

        softLinx.soloSoftRun(
            "C:\\Users\\svcaibio\\Dev\\liquidhandling\\protocols\\campaign2\\test_hso\\"
            + directory_name
            + "\\"
            + os.path.basename(treatment_to_assay_1_hso[k])
        )
        softLinx.soloSoftRun(
            "C:\\Users\\svcaibio\\Dev\\liquidhandling\\protocols\\campaign2\\test_hso\\"
            + directory_name
            + "\\"
            + os.path.basename(treatment_to_assay_2_hso[k])
        )
    

        softLinx.plateCraneMovePlate(["SoftLinx.Solo.Position4"], ["SoftLinx.Liconic.Nest"])
            #softLinx.hidexClose()
        softLinx.plateCraneReplaceLid(["SoftLinx.PlateCrane.LidNest2"], ["SoftLinx.Liconic.Nest"])
        softLinx.plateCraneMoveCrane("SoftLinx.PlateCrane.Safe")
        # Load plate into incubator
        softLinx.liconicLoadIncubator(loadID=k, holdWithoutIncubationTime=True)

        #TODO: swap out all labware? (dilution plates etc)
        #* END LOOP

    # reduce Hidex temp to reduce strain on instument over incubation (necessary?)
    softLinx.hidexRun("SetTemp20")

    softLinx.liconicShake(shaker1Speed=30, shakeTime=[0,7,6,0]) # 7hrs 6 min # * Temp shorten for testing

    # preheat Hidex for readings after incubation
    softLinx.hidexRun("SetTempWait37")

    #* LOOP: unload plates from incubator and take endpoing reading
    for k in range(len(treatment)):
        softLinx.liconicUnloadIncubator(loadID=k)
        softLinx.plateCraneRemoveLid(["SoftLinx.Liconic.Nest"], ["SoftLinx.PlateCrane.LidNest2"])
        softLinx.plateCraneMovePlate(["SoftLinx.Liconic.Nest"], ["SoftLinx.Hidex.Nest"])
        softLinx.hidexClose()
        softLinx.plateCraneMoveCrane("SoftLinx.PlateCrane.Safe")
        softLinx.hidexRun("Campaign1_noIncubate2") # TODO

        # transfer data to lambda6 # TODO
        softLinx.runProgram(
            "C:\\Users\\svcaibio\\Dev\\liquidhandling\\zeromq\\utils\\send_data.bat", arguments=f"{k} {directory_name} campaign2"
        )

        # Move plate from Hidex to Stack 1 and replace lid
        softLinx.plateCraneMovePlate(["SoftLinx.Hidex.Nest"], ["SoftLinx.PlateCrane.Stack1"])
        softLinx.hidexClose()
        softLinx.plateCraneReplaceLid(["SoftLinx.PlateCrane.LidNest2"], ["SoftLinx.PlateCrane.Stack1"])
        softLinx.plateCraneMoveCrane("SoftLinx.PlateCrane.Safe")

        # shake in incubator until time to take next reading  (don't do if already read last plate)
        if not k == (len(treatment)-1):
            softLinx.liconicShake(shaker1Speed=30, shakeTime=[0,0,23,0])  # 23 min
    #* END LOOP

    softLinx.hidexRun("SetTemp20")
    softLinx.liconicEndShake()
    # save protocol to write instructions to .slvp file, create .txt manifest, and .ahk remote start file
    softLinx.saveProtocol()

"""
    SEND NEW PROTOCOL TO WORK CELL (HUDSON01) ------------------------------------------------------------------
"""
#     try:
#         # TODO: change to full path on lambda6
#         child_message_sender = child_pid = Popen(
#             [
#                 "python",
#                 "../../zeromq/lambda6_send_instructions.py",
#                 "-d",
#                 directory_path,
#                 "-i",
#                 str(num_assay_plates),
#                 str(num_assay_wells),
#                 assay_plate_type,
#                 str(is_test),
#             ],
#             start_new_session=True,
#         ).pid

#         print("New instruction directory passed to lambda6_send_message.py")
#     except BaseException as e:
#         print(e)
#         print("Could not send new instructions to hudson01")

#     return return_val


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
    generate_campaign1_repeatable(
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

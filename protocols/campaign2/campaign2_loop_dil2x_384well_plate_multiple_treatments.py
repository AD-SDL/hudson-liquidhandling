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
from campaign2_loop_dil2x_384_multiple_treatments_functions import *

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

"""
Version to plate multiple treatments within the same 384 well plate (one per 6 column quadrant)
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
    # TODO: for future make variables treatment specific?
    blowoff_volume = 10
    num_mixes = 3
    media_z_shift = 0.5
    reservoir_z_shift = 0.5  # z shift for deep blocks (Deck Positions 3 and 5)
    flat_bottom_z_shift = 2  # Note: 1 is not high enough (tested)
    # lambda6_path = "/lambda_stor/data/hudson/instructions/"
    lambda6_path = "C:\\Users\\svcaibio\\Dev\\liquidhandling\\protocols\\campaign2\\test_hso\\" # TODO change directory name

    # Step 1 variables
    media_transfer_volume_s1 = 20 
    culture_transfer_volume_s1 = 10 # reducing volumes, keeping 1:3 ratio culture to media volume
    half_dilution_media_volume = 99
    dilution_culture_volume = 22
    culture_plate_mix_volume_s1 = 100  # mix volume increased for test 09/07/21
    culture_plate_num_mix = 7
    culture_dilution_num_mix = 10
    growth_plate_mix_volume_s1 = 20
    culture_dilution_mix_volume = 180

    # Step 2 variables
    media_transfer_volume_s2 = ( # TODO: increase most stock volumes for 384
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
    antibiotic_mix_volume_s3 = 30
    destination_mix_volume_s3 = 50

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
    # TODO: should be able to keep the same? but look into it
    media_to_assay_1_hso = []
    # media_to_assay_2_hso = []
    # media_to_assay_3_hso = []
    # media_to_assay_4_hso = []
    media_to_culture_hso = []
    cells_to_assay_hso = []
    # cells_to_assay_2_hso = []
    serial_dilution_hso = []
    treatment_to_assay_hso = []
    # treatment_to_assay_2_hso = []

    #* LOOP: produce 8 separate .hso files per treatment
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
        media_to_assay_1_hso.append(generate_media_transfer_to_quarter_assay_hso(directory_path=directory_path,
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
        fielname="media_to_culture",
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

        #* add diluted cells to assay # one column of tips unless want to do outside of loop?
        #* no loop, so that we can blowoff
        cells_to_assay_hso.append(generate_add_diluted_cells_to_assay_hso(directory_path=directory_path,
        filename="cells_to_assay",
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


        #* perform serial dilution of given treatment # one column of tips
        #* should be fine to leave same? just increase volumes
        serial_dilution_hso.append(generate_serial_dlution_treatment_hso(directory_path=directory_path,
        filename="treatment_serial_dilution",
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
        filename="treatment_to_assay",
        treatment_dil_half=treatment_dil_half,
        antibiotic_transfer_volume_s3=antibiotic_transfer_volume_s3,
        num_mixes=num_mixes,
        antibiotic_mix_volume_s3=antibiotic_mix_volume_s3,
        reservoir_z_shift=reservoir_z_shift,
        destination_mix_volume_s3=destination_mix_volume_s3,
        flat_bottom_z_shift=flat_bottom_z_shift,
        start_col=1,
        end_col=6,
        k=k,
        reservoir_z_shift=reservoir_z_shift))

        # TODO: tip total per treatment: 5, can use 2 boxes per treatment as of now
    
    # * ADD TO SOFTLINX PIPELINE

    # initialize softLinx
    softLinx = SoftLinx("Steps_384_assay_multi_treatment", os.path.join(directory_path, "steps384_assay_multi_treatment.slvp"))

    # softLinx.setPlates(
    #     {"SoftLinx.PlateCrane.Stack5": "Corning 3540", }
    # )

    softLinx.setPlates(
        {"SoftLinx.PlateCrane.Stack5": "Plate.96.Corning-3635.ClearUVAssay", "SoftLinx.PlateCrane.Stack4": "TipBox.180uL.Axygen-EVF-180-R-S.bluebox"}
    )

    # set up equiptment
    softLinx.hidexRun("SetTemp37")
    softLinx.liconicBeginShake(shaker1Speed=30)

    #* loop over treatments, every four treatments, swap out assay plate from stack 5 to position 4

        #* replace tip box every two treatments

        #* run all liquid handling steps for current treatment

        #* if fourth or last treatment total, move assay plate from position 4 to liconic, replace lid, move to safe, load incubator

    #* incubate plates for 12 hours, start up hidex

    #TODO: create way to detemrine how many plates we have (#treatments/4)

    #* range over plates, take hidex readings


    #TODO: lambda6 path

        
    









    







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


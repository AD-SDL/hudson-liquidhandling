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
    lambda6_path = "/lambda_stor/data/hudson/instructions/"

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

    #* LOOP: produce 3 separate .hso files per plate
    for k in range(len(treatment)):
        # * Get location of treatment
        try:
            treatment_plate_loc, treatment_column = find_treatment_loc(treatment[k])
        except Error as e:
            print(f"Unable to locate treatment {treatment[k]}")
            raise  # need to know locaton of treatment, rest of protocol useless if not specified



        ''' CALL generate_media_transfer_to_assay_hso TWICE, ONE FOR EACH HALF OF PLATE, change start and end cols'''
        media_to_assay_1_hso.append(campaign2_loop_dil2x_tiprep_384well_plate_hso_functions.generate_media_transfer_to_half_assay_hso(directory_path=directory_path,
media_start_column=media_start_column,
media_z_shift=media_z_shift, 
media_transfer_volume_s1=media_transfer_volume_s1,
flat_bottom_z_shift=flat_bottom_z_shift,
start_col = 1,
end_col = 6,
k=k))

        media_to_assay_2_hso.append(campaign2_loop_dil2x_tiprep_384well_plate_hso_functions.generate_media_transfer_to_half_assay_hso(directory_path=directory_path,
media_start_column=media_start_column,
media_z_shift=media_z_shift, 
media_transfer_volume_s1=media_transfer_volume_s1,
flat_bottom_z_shift=flat_bottom_z_shift,
start_col = 7,
end_col = 12,
k=k))


        ''' call generate_fill_culture_dilution_and_treatment_plates_with_media_hso'''

        media_to_culture_hso.append(campaign2_loop_dil2x_tiprep_384well_plate_hso_functions.generate_fill_culture_dilution_and_treatment_plates_with_media_hso(directory_path=directory_path,
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
        cells_to_assay_1_hso.append(campaign2_loop_dil2x_tiprep_384well_plate_hso_functions.generate_add_diluted_cells_to_assay_hso(directory_path=directory_path,
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

        cells_to_assay_2_hso.append(campaign2_loop_dil2x_tiprep_384well_plate_hso_functions.generate_add_diluted_cells_to_assay_hso(directory_path=directory_path,
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

        serial_dilution_hso.append(campaign2_loop_dil2x_tiprep_384well_plate_hso_functions.generate_serial_dlution_treatment_hso(directory_path=directory_path,
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
        
        treatment_to_assay_1_hso.append(campaign2_loop_dil2x_tiprep_384well_plate_hso_functions.generate_add_antibioitc_to_assay_hso(directory_path=directory_path,
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

        treatment_to_assay_1_hso.append(campaign2_loop_dil2x_tiprep_384well_plate_hso_functions.generate_add_antibioitc_to_assay_hso(directory_path=directory_path,
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

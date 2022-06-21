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

    step1_hso_filename_list = []
    step2_hso_filename_list = []
    step3_hso_filename_list = []

 # * Transfers media from resevoir in position 1 to given columns in 384 well assay plate in position 4
    def generate_media_transfer_to_half_assay_hso(directory_path, 
    step1_hso_filename_list,
    media_start_column,
    media_z_shift, 
    media_transfer_volume_s1,
    flat_bottom_z_shift
    start_col, # provide column to start dispense on assay plate
    end_col): # provide column to end dispense on assay plate


        # * Initialize soloSoft (step 1)
        step1_hso_filename = os.path.join(directory_path, f"plate{k}_step1.hso")
        #step1_hso_filename_list.append(step1_hso_filename)
        soloSoft = SoloSoft(
            filename=step1_hso_filename,
            plateList=[
                "DeepBlock.96.VWR-75870-792.sterile",
                "Empty",
                "TipBox.180uL.Axygen-EVF-180-R-S.bluebox",
                "Corning 3540",
                "DeepBlock.96.VWR-75870-792.sterile",
                "DeepBlock.96.VWR-75870-792.sterile",
                "DeepBlock.96.VWR-75870-792.sterile",
                "DeepBlock.96.VWR-75870-792.sterile",
            ],
        )

        soloSoft.getTip("Position3")

        for i in range(start_col, end_col+1):  # first quarter plate = media from column 1
            soloSoft.aspirate(
                position="Position1",
                aspirate_volumes=Reservoir_12col_Agilent_201256_100_BATSgroup().setColumn(
                    media_start_column[k], media_transfer_volume_s1
                ),
                aspirate_shift=[0, 0, media_z_shift],
            )
            soloSoft.dispense(
                position="Position4",
                dispense_volumes=Plate_384_Corning_3540_BlackwClearBottomAssay().setColumn(
                    i, media_transfer_volume_s1
                ),
                dispense_shift=[0, 0, flat_bottom_z_shift],
            )

            soloSoft.aspirate(
                position="Position1",
                aspirate_volumes=Reservoir_12col_Agilent_201256_100_BATSgroup().setColumn(
                    media_start_column[k], media_transfer_volume_s1
                ),
                aspirate_shift=[0, 0, media_z_shift],
            )
            dispense_volumes_startB = Plate_384_Corning_3540_BlackwClearBottomAssay().setColumn(
                    i, media_transfer_volume_s1
                )
            dispense_volumes_startB[0][i-1] = 0
            soloSoft.dispense(
                position="Position4",
                dispense_volumes= dispense_volumes_startB,
                dispense_shift=[0, 0, flat_bottom_z_shift],
            )
           
        for i in range(start_col+6, end_col+7):  # second quarter plate = media from column 2
            soloSoft.aspirate(
                position="Position1",
                aspirate_volumes=Reservoir_12col_Agilent_201256_100_BATSgroup().setColumn(
                    media_start_column[k] + 1, media_transfer_volume_s1
                ),
                aspirate_shift=[0, 0, media_z_shift],
            )
            soloSoft.dispense(
                position="Position4",
                dispense_volumes=Plate_384_Corning_3540_BlackwClearBottomAssay().setColumn(
                    i, media_transfer_volume_s1
                ),
                dispense_shift=[0, 0, flat_bottom_z_shift],
            )

            soloSoft.aspirate(
                position="Position1",
                aspirate_volumes=Reservoir_12col_Agilent_201256_100_BATSgroup().setColumn(
                    media_start_column[k] + 1, media_transfer_volume_s1
                ),
                aspirate_shift=[0, 0, media_z_shift],
            )
            dispense_volumes_startB = Plate_384_Corning_3540_BlackwClearBottomAssay().setColumn(
                    i, media_transfer_volume_s1
                )
            dispense_volumes_startB[0][i-1] = 0
            soloSoft.dispense(
                position="Position4",
                dispense_volumes= dispense_volumes_startB,
                dispense_shift=[0, 0, flat_bottom_z_shift],
            )

        soloSoft.shuckTip()
        soloSoft.savePipeline()

        hudson01_hso_path = # * TODO: FIGURE OUT PATH NAME

        return hudson01_hso_path

    # * Fill culture dilution resevoir and treatment plates with media
    def generate_fill_culture_dilution_and_treatment_plates_with_media_hso(directory_path, 
    step1_hso_filename_list,
    media_start_column,
    media_z_shift,
    flat_bottom_z_shift,
    reservoir_z_shift,
    half_dilution_media_volume,
    dilution_culture_volume,
    culture_plate_num_mix,
    culture_plate_mix_volume_s1,
    culture_dil_column
    ):
        step1_cell_dilution_hso_filename = os.path.join(directory_path, f"plate{k}_step1_cell_dilution.hso")
        #step1_hso_filename_list.append(step1_cell_dilution_hso_filename)
        soloSoft = SoloSoft(
            filename=step1_cell_dilution_hso_filename,
            plateList=[
                "DeepBlock.96.VWR-75870-792.sterile",
                "Empty",
                "TipBox.180uL.Axygen-EVF-180-R-S.bluebox",
                "Corning 3540",
                "DeepBlock.96.VWR-75870-792.sterile",
                "DeepBlock.96.VWR-75870-792.sterile",
                "DeepBlock.96.VWR-75870-792.sterile",
                "DeepBlock.96.VWR-75870-792.sterile",
            ],
        )

        soloSoft.getTip("Position3")


        # * Fill one column of culture dilution plate with fresh lb media (do in two steps due to 180uL filter tips)
        for i in range(
            2
        ):  # from first media column -> cell dilution plate, column = same as culture column
            soloSoft.aspirate(
                position="Position1",
                aspirate_volumes=Reservoir_12col_Agilent_201256_100_BATSgroup().setColumn(
                    media_start_column[k], half_dilution_media_volume
                ),
                aspirate_shift=[0, 0, media_z_shift],
            )
            soloSoft.dispense(
                position="Position7",
                dispense_volumes=Reservoir_12col_Agilent_201256_100_BATSgroup().setColumn(
                    culture_dil_column[k], half_dilution_media_volume
                ),
                dispense_shift=[0, 0, reservoir_z_shift],
            )

        for i in range(
            2
        ):  # from second media column -> cell dilution plate
            soloSoft.aspirate(
                position="Position1",
                aspirate_volumes=Reservoir_12col_Agilent_201256_100_BATSgroup().setColumn(
                    media_start_column[k] + 1, half_dilution_media_volume
                ),
                aspirate_shift=[0, 0, media_z_shift],
            )
            soloSoft.dispense(
                position="Position7",
                dispense_volumes=Reservoir_12col_Agilent_201256_100_BATSgroup().setColumn(
                    culture_dil_column[k], half_dilution_media_volume
                ),
                dispense_shift=[0, 0, reservoir_z_shift],
            )

        # * Make culture 10 fold dilution
        for i in range(1, 3):  # all cells dispensed into same cell dilution column
            soloSoft.aspirate(
                position="Position5",
                aspirate_volumes=DeepBlock_96VWR_75870_792_sterile().setColumn(
                    culture_column[k], dilution_culture_volume
                ),
                aspirate_shift=[0, 0, 2],
                mix_at_start=True,
                mix_cycles=culture_plate_num_mix,
                mix_volume=culture_plate_mix_volume_s1,
                dispense_height=2,
                # pre_aspirate=blowoff_volume,
                syringe_speed=25,
            )
            soloSoft.dispense(
                position="Position7",
                dispense_volumes=Reservoir_12col_Agilent_201256_100_BATSgroup().setColumn(
                    culture_dil_column[k], dilution_culture_volume
                ),
                dispense_shift=[0, 0, reservoir_z_shift],
                mix_at_finish=True,
                mix_cycles=num_mixes,
                mix_volume=culture_plate_mix_volume_s1,
                aspirate_height=reservoir_z_shift,
                syringe_speed=25,
                # blowoff=blowoff_volume,
            )

        # * Separate big mix step to ensure cell diluton column is well mixed  # added for 09/07/21
        soloSoft.aspirate(
            position="Position7",
            aspirate_volumes=Reservoir_12col_Agilent_201256_100_BATSgroup().setColumn(
                culture_dil_column[k], dilution_culture_volume
            ),
            aspirate_shift=[0, 0, reservoir_z_shift],
            # 100% syringe speed
        )
        soloSoft.dispense(
            position="Position7",
            dispense_volumes=Reservoir_12col_Agilent_201256_100_BATSgroup().setColumn(
                culture_dil_column[k], dilution_culture_volume
            ),
            dispense_shift=[0, 0, reservoir_z_shift],
            mix_at_finish=True,
            mix_cycles=culture_dilution_num_mix,
            mix_volume=culture_dilution_mix_volume,
            aspirate_height=reservoir_z_shift,
            syringe_speed=75,
            # blowoff=blowoff_volume,
        )

        soloSoft.shuckTip()
        soloSoft.savePipeline()

        return filename

    # * Adds diluted cells to assay plate
    def generate_add_diluted_cells_to_assay_hso(directory_path, 
    step1_hso_filename_list,
    media_start_column,
    media_z_shift,
    flat_bottom_z_shift,
    reservoir_z_shift,
    culture_transfer_volume_s1,
    culture_dil_column,
    num_mixes,
    growth_plate_mix_volume_s1,
    start_col,
    end_col
    ):
        step1_cells_to_assay_first_half_hso_filename = os.path.join(directory_path, f"plate{k}_step1_cells_to_assay_first_half.hso")
        step1_hso_filename_list.append(step1_cells_to_assay_first_half_hso_filename)
        soloSoft = SoloSoft(
            filename=step1_cells_to_assay_first_half_hso_filename,
            plateList=[
                "DeepBlock.96.VWR-75870-792.sterile",
                "Empty",
                "TipBox.180uL.Axygen-EVF-180-R-S.bluebox",
                "Corning 3540",
                "DeepBlock.96.VWR-75870-792.sterile",
                "DeepBlock.96.VWR-75870-792.sterile",
                "DeepBlock.96.VWR-75870-792.sterile",
                "DeepBlock.96.VWR-75870-792.sterile",
            ],
        )

        # * Add bacteria from 10 fold diluted culture plate (Position 7, column = culture_column[k]) to growth plate with fresh media (both halves)
        soloSoft.getTip("Position3")
        for i in range(start_col, end_col+1):  # trying a different method of cell dispensing (09/07/21)
            soloSoft.aspirate(  # well in first half
                position="Position7",
                aspirate_volumes=Reservoir_12col_Agilent_201256_100_BATSgroup().setColumn(
                    culture_dil_column[k], culture_transfer_volume_s1
                ),
                aspirate_shift=[
                    0,
                    0,
                    reservoir_z_shift,
                ],
                mix_at_start=True,
                mix_cycles=num_mixes,
                dispense_height=reservoir_z_shift,
                mix_volume=culture_transfer_volume_s1,
                syringe_speed=25,
            )
            soloSoft.dispense(  # do need to mix at end of transfer
                position="Position4",
                dispense_volumes=Plate_384_Corning_3540_BlackwClearBottomAssay().setColumn(
                    i, culture_transfer_volume_s1
                ),
                mix_at_finish=True,
                mix_cycles=num_mixes,
                mix_volume=growth_plate_mix_volume_s1,
                aspirate_height=flat_bottom_z_shift,
                dispense_shift=[0, 0, flat_bottom_z_shift],
                syringe_speed=25,
            )

            soloSoft.aspirate(  # well in first half
                position="Position7",
                aspirate_volumes=Reservoir_12col_Agilent_201256_100_BATSgroup().setColumn(
                    culture_dil_column[k], culture_transfer_volume_s1
                ),
                aspirate_shift=[
                    0,
                    0,
                    reservoir_z_shift,
                ],
                mix_at_start=True,
                mix_cycles=num_mixes,
                dispense_height=reservoir_z_shift,
                mix_volume=culture_transfer_volume_s1,
                syringe_speed=25,
            )

            dispense_volumes_startB = Plate_384_Corning_3540_BlackwClearBottomAssay().setColumn(
                    i, culture_transfer_volume_s1
                )
            dispense_volumes_startB[0][i-1] = 0

            soloSoft.dispense(  # do need to mix at end of transfer
                position="Position4",
                dispense_volumes=dispense_volumes_startB,
                mix_at_finish=True,
                mix_cycles=num_mixes,
                mix_volume=growth_plate_mix_volume_s1,
                aspirate_height=flat_bottom_z_shift,
                dispense_shift=[0, 0, flat_bottom_z_shift],
                syringe_speed=25,
            )

            soloSoft.aspirate(  # well in second half
                position="Position7",
                aspirate_volumes=Reservoir_12col_Agilent_201256_100_BATSgroup().setColumn(
                    culture_dil_column[k], culture_transfer_volume_s1
                ),
                aspirate_shift=[
                    0,
                    0,
                    reservoir_z_shift,
                ],
                mix_at_start=True,
                mix_cycles=num_mixes,
                dispense_height=reservoir_z_shift,
                mix_volume=culture_transfer_volume_s1,
                syringe_speed=25,
            )
            soloSoft.dispense(  # do need to mix at end of transfer
                position="Position4",
                dispense_volumes=Plate_384_Corning_3540_BlackwClearBottomAssay().setColumn(
                    6 + i, culture_transfer_volume_s1
                ),
                mix_at_finish=True,
                mix_cycles=num_mixes,
                mix_volume=growth_plate_mix_volume_s1,
                aspirate_height=flat_bottom_z_shift,
                dispense_shift=[0, 0, flat_bottom_z_shift],
                syringe_speed=25,
            )
            soloSoft.aspirate(  # well in second half
                position="Position7",
                aspirate_volumes=Reservoir_12col_Agilent_201256_100_BATSgroup().setColumn(
                    culture_dil_column[k], culture_transfer_volume_s1
                ),
                aspirate_shift=[
                    0,
                    0,
                    reservoir_z_shift,
                ],
                mix_at_start=True,
                mix_cycles=num_mixes,
                dispense_height=reservoir_z_shift,
                mix_volume=culture_transfer_volume_s1,
                syringe_speed=25,
            )
            dispense_volumes_startB = Plate_384_Corning_3540_BlackwClearBottomAssay().setColumn(
                    6 + i, culture_transfer_volume_s1
                )
            dispense_volumes_startB[0][i+5] = 0

            soloSoft.dispense(  # do need to mix at end of transfer
                position="Position4",
                dispense_volumes=dispense_volumes_startB,
                mix_at_finish=True,
                mix_cycles=num_mixes,
                mix_volume=growth_plate_mix_volume_s1,
                aspirate_height=flat_bottom_z_shift,
                dispense_shift=[0, 0, flat_bottom_z_shift],
                syringe_speed=25,
            )
        
        soloSoft.shuckTip()
        soloSoft.savePipeline()

        return filename

    #* Step 2, performs serial dilution on treatment plate
    def generate_serial_dlution_treatment_hso(directory_path, 
    step2_hso_filename_list,
    treatment_dil_half,
    media_start_column,
    media_transfer_volume_s2,
    media_z_shift,
    reservoir_z_shift,
    last_column_transfer_volume_s2,
    treatment_plate_loc,
    serial_antibiotic_transfer_volume_s2,
    treatment_column,
    blowoff_volume,
    serial_source_num_mixes_s2,
    serial_source_mixing_volume_s2,
    serial_destination_mixing_volume_s2,
    ):

         # * Initialize soloSoft (step 2)
        step2_hso_filename = os.path.join(directory_path, f"plate{k}_step2.hso")
        step2_hso_filename_list.append(step2_hso_filename)
        soloSoft = SoloSoft(
            filename=step2_hso_filename,
            plateList=[
                "DeepBlock.96.VWR-75870-792.sterile",
                "Empty",
                "TipBox.180uL.Axygen-EVF-180-R-S.bluebox",
                "Corning 3540",
                "DeepBlock.96.VWR-75870-792.sterile",
                "DeepBlock.96.VWR-75870-792.sterile",
                "DeepBlock.96.VWR-75870-792.sterile",
                "DeepBlock.96.VWR-75870-792.sterile",
            ],
        )

        # * Fill colums 1-5 of generic 96 well plate with 216uL lb media in two steps (will use for both halves of plate)
        soloSoft.getTip("Position3")
        for i in range(
            (6 * (treatment_dil_half[k] - 1)) + 1, (6 * (treatment_dil_half[k] - 1)) + 6
        ):  # columns 1-5 or columns 7-11 (treatment_dil_half = 1 or 2)
            # draws from both lb media wells to prevent running out of media
            soloSoft.aspirate(  # 120 from first lb media well
                position="Position1",
                aspirate_volumes=Reservoir_12col_Agilent_201256_100_BATSgroup().setColumn(
                    media_start_column[k], media_transfer_volume_s2
                ),
                aspirate_shift=[0, 0, media_z_shift],
                # pre_aspirate=blowoff_volume,
            )
            soloSoft.dispense(
                position="Position6",
                dispense_volumes=Reservoir_12col_Agilent_201256_100_BATSgroup().setColumn(
                    i, media_transfer_volume_s2
                ),
                dispense_shift=[0, 0, reservoir_z_shift],
                # blowoff=blowoff_volume,
            )

            soloSoft.aspirate(  # 120 from second lb media well
                position="Position1",
                aspirate_volumes=Reservoir_12col_Agilent_201256_100_BATSgroup().setColumn(
                    media_start_column[k] + 1, media_transfer_volume_s2
                ),
                aspirate_shift=[0, 0, media_z_shift],
                # pre_aspirate=blowoff_volume,
            )
            soloSoft.dispense(
                position="Position6",
                dispense_volumes=Reservoir_12col_Agilent_201256_100_BATSgroup().setColumn(
                    i, media_transfer_volume_s2
                ),
                dispense_shift=[0, 0, reservoir_z_shift],
                # blowoff=blowoff_volume,
            )

        
        # * Fill column 6 of a generic 96 well plate with 240uL lb media total in two steps
        for i in range(media_start_column[k], media_start_column[k] + 2):
            soloSoft.aspirate(  # first lb media well
                position="Position1",
                aspirate_volumes=Reservoir_12col_Agilent_201256_100_BATSgroup().setColumn(
                    i, last_column_transfer_volume_s2
                ),
                aspirate_shift=[0, 0, media_z_shift],
                # pre_aspirate=blowoff_volume,
            )
            soloSoft.dispense(
                position="Position6",
                dispense_volumes=Reservoir_12col_Agilent_201256_100_BATSgroup().setColumn(
                    (6 * (treatment_dil_half[k] - 1)) + 6, last_column_transfer_volume_s2
                ),
                dispense_shift=[0, 0, reservoir_z_shift],
                # blowoff=blowoff_volume,
            )

        # * Transfer treatment in to first column of treatement dilution plate (will make 1:2 dilution)
        for i in range(2):
            soloSoft.aspirate(
                position=treatment_plate_loc,
                aspirate_volumes=Reservoir_12col_Agilent_201256_100_BATSgroup().setColumn(
                    treatment_column, serial_antibiotic_transfer_volume_s2
                ),
                pre_aspirate=blowoff_volume,
                mix_at_start=True,
                mix_cycles=serial_source_num_mixes_s2,
                mix_volume=serial_source_mixing_volume_s2,
                aspirate_shift=[0, 0, reservoir_z_shift],
                dispense_height=reservoir_z_shift,
            )
            soloSoft.dispense(
                position="Position6",
                dispense_volumes=Reservoir_12col_Agilent_201256_100_BATSgroup().setColumn(
                    (6 * (treatment_dil_half[k] - 1)) + 1, serial_antibiotic_transfer_volume_s2
                ),
                dispense_shift=[0, 0, reservoir_z_shift],
                blowoff=blowoff_volume,
                # mix_at_finish=True,
                # mix_cycles=num_mixes,
                # mix_volume=serial_destination_mixing_volume_s2,
                aspirate_height=reservoir_z_shift,
            )

        # * Serial dilution within Generic 96 well plate (Corning or Falcon) - mix 3 times before and after transfer
        for i in range(
            (6 * (treatment_dil_half[k] - 1)) + 1, (6 * (treatment_dil_half[k] - 1)) + 5
        ):  # don't serial dilute into the last column (control column)
            # if i == 4:  # switch tips half way through to reduce error   #TODO: Test if you need this
            #     soloSoft.getTip()
            for j in range(2):
                soloSoft.aspirate(
                    position="Position6",
                    aspirate_volumes=Reservoir_12col_Agilent_201256_100_BATSgroup().setColumn(
                        i, serial_antibiotic_transfer_volume_s2
                    ),
                    aspirate_shift=[0, 0, reservoir_z_shift],
                    pre_aspirate=blowoff_volume,
                    mix_at_start=True,
                    mix_cycles=num_mixes,
                    mix_volume=serial_destination_mixing_volume_s2,
                    dispense_height=reservoir_z_shift,
                )
                soloSoft.dispense(
                    position="Position6",
                    dispense_volumes=Reservoir_12col_Agilent_201256_100_BATSgroup().setColumn(
                        i + 1, serial_antibiotic_transfer_volume_s2
                    ),
                    dispense_shift=[0, 0, reservoir_z_shift],
                    blowoff=blowoff_volume,
                    mix_at_finish=True,
                    mix_cycles=num_mixes,
                    mix_volume=serial_destination_mixing_volume_s2,
                    aspirate_height=reservoir_z_shift,
                )
        # no need to throw away excess volume from last column of serial dilution

        soloSoft.shuckTip()
        soloSoft.savePipeline()

        return filename

    # * adds antibiotic to assay plate
    def generate_add_antibioitc_to_assay_hso(directory_path, 
    step3_hso_filename_list,
    treatment_dil_half,
    antibiotic_transfer_volume_s3,
    num_mixes,
    antibiotic_mix_volume_s3,
    resevoir_z_shift,
    destination_mix_volume_s3,
    flat_bottom_z_shift,
    start_col,
    end_col
    ):
        step3_hso_filename = os.path.join(directory_path, f"plate{k}_step3.hso")
        step3_hso_filename_list.append(step3_hso_filename)
        soloSoft = SoloSoft(
            filename=step3_hso_filename,
            plateList=[
                "DeepBlock.96.VWR-75870-792.sterile",
                "Empty",
                "TipBox.180uL.Axygen-EVF-180-R-S.bluebox",
                "Corning 3540",
                "DeepBlock.96.VWR-75870-792.sterile",
                "DeepBlock.96.VWR-75870-792.sterile",
                "DeepBlock.96.VWR-75870-792.sterile",
                "DeepBlock.96.VWR-75870-792.sterile",
            ],
        )

        soloSoft.getTip("Position3")
        for i in range(end_col, start_col-1, -1):  # first quarter of plate
            # if i == 3:  # switch tips half way through to reduce error  # tested and ok to remove
            #     soloSoft.getTip()
            soloSoft.aspirate(
                position="Position6",
                aspirate_volumes=Reservoir_12col_Agilent_201256_100_BATSgroup().setColumn(
                    (6 * (treatment_dil_half[k] - 1)) + i, antibiotic_transfer_volume_s3
                ),
                mix_at_start=True,
                mix_cycles=num_mixes,
                mix_volume=antibiotic_mix_volume_s3,
                dispense_height=reservoir_z_shift,
                aspirate_shift=[0, 0, reservoir_z_shift],
            )
            soloSoft.dispense(
                position="Position4",
                dispense_volumes=Plate_384_Corning_3540_BlackwClearBottomAssay().setColumn(
                    i, antibiotic_transfer_volume_s3
                ),
                mix_at_finish=True,
                mix_cycles=num_mixes,
                mix_volume=destination_mix_volume_s3,
                aspirate_height=flat_bottom_z_shift,
                dispense_shift=[0, 0, flat_bottom_z_shift],
            )

            soloSoft.aspirate(
                position="Position6",
                aspirate_volumes=Reservoir_12col_Agilent_201256_100_BATSgroup().setColumn(
                    (6 * (treatment_dil_half[k] - 1)) + i, antibiotic_transfer_volume_s3
                ),
                mix_at_start=True,
                mix_cycles=num_mixes,
                mix_volume=antibiotic_mix_volume_s3,
                dispense_height=reservoir_z_shift,
                aspirate_shift=[0, 0, reservoir_z_shift],
            )

            dispense_volumes_startB = Plate_384_Corning_3540_BlackwClearBottomAssay().setColumn(
                    i, antibiotic_transfer_volume_s3
                )
            dispense_volumes_startB[0][i-1] = 0

            soloSoft.dispense(
                position="Position4",
                dispense_volumes=dispense_volumes_startB,
                mix_at_finish=True,
                mix_cycles=num_mixes,
                mix_volume=destination_mix_volume_s3,
                aspirate_height=flat_bottom_z_shift,
                dispense_shift=[0, 0, flat_bottom_z_shift],
            )

        soloSoft.getTip("Position3")
        for i in range(end_col, start_col-1, -1):  # second quarter of plate
            # if i == 3:  # switch tips half way through to reduce error  # tested and ok to remove
            #     soloSoft.getTip()
            soloSoft.aspirate(
                position="Position6",
                aspirate_volumes=Reservoir_12col_Agilent_201256_100_BATSgroup().setColumn(
                    (6 * (treatment_dil_half[k] - 1)) + i, antibiotic_transfer_volume_s3
                ),
                mix_at_start=True,
                mix_cycles=num_mixes,
                mix_volume=antibiotic_mix_volume_s3,
                dispense_height=reservoir_z_shift,
                aspirate_shift=[0, 0, reservoir_z_shift],
            )
            soloSoft.dispense(
                position="Position4",
                dispense_volumes=Plate_384_Corning_3540_BlackwClearBottomAssay().setColumn(
                    i + 6, antibiotic_transfer_volume_s3
                ),
                mix_at_finish=True,
                mix_cycles=num_mixes,
                mix_volume=destination_mix_volume_s3,
                aspirate_height=flat_bottom_z_shift,
                dispense_shift=[0, 0, flat_bottom_z_shift],
            )
            soloSoft.aspirate(
                position="Position6",
                aspirate_volumes=Reservoir_12col_Agilent_201256_100_BATSgroup().setColumn(
                    (6 * (treatment_dil_half[k] - 1)) + i, antibiotic_transfer_volume_s3
                ),
                mix_at_start=True,
                mix_cycles=num_mixes,
                mix_volume=antibiotic_mix_volume_s3,
                dispense_height=reservoir_z_shift,
                aspirate_shift=[0, 0, reservoir_z_shift],
            )
            dispense_volumes_startB = Plate_384_Corning_3540_BlackwClearBottomAssay().setColumn(
                    i + 6, antibiotic_transfer_volume_s3
                )
            dispense_volumes_startB[0][i+5] = 0

            soloSoft.dispense(
                position="Position4",
                dispense_volumes=dispense_volumes_startB,
                mix_at_finish=True,
                mix_cycles=num_mixes,
                mix_volume=destination_mix_volume_s3,
                aspirate_height=flat_bottom_z_shift,
                dispense_shift=[0, 0, flat_bottom_z_shift],
            )

        soloSoft.shuckTip()
        soloSoft.savePipeline()

        return filename

    #* LOOP: produce 3 separate .hso files per plate
    for k in range(len(treatment)):
        # * Get location of treatment
        try:
            treatment_plate_loc, treatment_column = find_treatment_loc(treatment[k])
        except Error as e:
            print(f"Unable to locate treatment {treatment[k]}")
            raise  # need to know locaton of treatment, rest of protocol useless if not specified

        ''' CALL generate_media_transfer_to_assay_hso TWICE, ONE FOR EACH HALF OF PLATE, change start and end cols'''

        ''' call generate_fill_culture_dilution_and_treatment_plates_with_media_hso'''

        '''call generate_add_diluted_cells_to_assay_hso twice, once for each half, change start and end cols'''

        ''' call generate_serial_dlution_treatment_hso'''

        '''call generate_add_antibioitc_to_assay_hso TWICE, for each half, different start_col, end_col'''
        




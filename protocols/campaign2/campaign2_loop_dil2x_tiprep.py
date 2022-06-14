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

created 01/05/22

SOLO DECK ARRANGEMENT: 
Pos 1 = 96 deep well media reservoir
Pos 2 = EMPTY (heat nest)
Pos 3 = 180uL tips (filtered if possible)
Pos 4 = EMPTY TO START 
Pos 5 = 96 deep well culture stock plate
Pos 6 = 96 deep well (empty at start)
Pos 7 = 96 deep well culture dilution plate (plate is empty at start)
Pos 8 = 96 well flat bottom treatment plate (one treatment per column, min 280uL treatment per well)

Stack 5 - 96 well clear, flat-bottom plate w/ lid.  (will be placed on deck pos 4 at start of protocol)
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
    media_transfer_volume_s1 = 60
    culture_transfer_volume_s1 = 30
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
    antibiotic_transfer_volume_s3 = 90
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
    num_assay_wells = 96  # hardcoded for now
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

    #* LOOP: produce 3 separate .hso files per plate
    for k in range(len(treatment)):
        # * Get location of treatment
        try:
            treatment_plate_loc, treatment_column = find_treatment_loc(treatment[k])
        except Error as e:
            print(f"Unable to locate treatment {treatment[k]}")
            raise  # need to know locaton of treatment, rest of protocol useless if not specified

        """
        STEP 1: INNOCULATE GROWTH PLATE FROM SOURCE BACTERIA PLATE -----------------------------------------------------------------
        """
        # * Initialize soloSoft (step 1)
        step1_hso_filename = os.path.join(directory_path, f"plate{k}_step1.hso")
        step1_hso_filename_list.append(step1_hso_filename)
        soloSoft = SoloSoft(
            filename=step1_hso_filename,
            plateList=[
                "DeepBlock.96.VWR-75870-792.sterile",
                "Empty",
                "TipBox.180uL.Axygen-EVF-180-R-S.bluebox",
                "Plate.96.Corning-3635.ClearUVAssay",
                "DeepBlock.96.VWR-75870-792.sterile",
                "DeepBlock.96.VWR-75870-792.sterile",
                "DeepBlock.96.VWR-75870-792.sterile",
                "DeepBlock.96.VWR-75870-792.sterile",
            ],
        )

        # * Fill all columns of empty 96 well plate (corning 3383 or Falcon - ref 353916) with fresh lb media (12 channel in Position 3, media_start_column and media_start_column+1)
        soloSoft.getTip("Position3")  
        j = 1
        for i in range(1, 7):  # first half plate = media from column 1
            soloSoft.aspirate(
                position="Position1",
                aspirate_volumes=Reservoir_12col_Agilent_201256_100_BATSgroup().setColumn(
                    media_start_column[k], media_transfer_volume_s1
                ),
                aspirate_shift=[0, 0, media_z_shift],
            )
            soloSoft.dispense(
                position="Position4",
                dispense_volumes=Plate_96_Corning_3635_ClearUVAssay().setColumn(
                    i, media_transfer_volume_s1
                ),
                dispense_shift=[0, 0, flat_bottom_z_shift],
            )

        for i in range(7, 13):  # second half plate = media from column 2
            soloSoft.aspirate(
                position="Position1",
                aspirate_volumes=Reservoir_12col_Agilent_201256_100_BATSgroup().setColumn(
                    media_start_column[k] + 1, media_transfer_volume_s1
                ),
                aspirate_shift=[0, 0, media_z_shift],
            )
            soloSoft.dispense(
                position="Position4",
                dispense_volumes=Plate_96_Corning_3635_ClearUVAssay().setColumn(
                    i, media_transfer_volume_s1
                ),
                dispense_shift=[0, 0, flat_bottom_z_shift],
            )

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

        # * Add bacteria from 10 fold diluted culture plate (Position 7, column = culture_column[k]) to growth plate with fresh media (both halves)
        soloSoft.getTip("Position3")  
        for i in range(1, 7):  # trying a different method of cell dispensing (09/07/21)
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
                dispense_volumes=Plate_96_Corning_3635_ClearUVAssay().setColumn(
                    i, culture_transfer_volume_s1
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
            soloSoft.dispense(  # do need to mix at end of transfer
                position="Position4",
                dispense_volumes=Plate_96_Corning_3635_ClearUVAssay().setColumn(
                    6 + i, culture_transfer_volume_s1
                ),
                mix_at_finish=True,
                mix_cycles=num_mixes,
                mix_volume=growth_plate_mix_volume_s1,
                aspirate_height=flat_bottom_z_shift,
                dispense_shift=[0, 0, flat_bottom_z_shift],
                syringe_speed=25,
            )

        soloSoft.shuckTip()
        soloSoft.savePipeline()

        """
        STEP 2: PERFORM SERIAL DILUTIONS ON TREATMENT -------------------------------------------------------------------------------
        """
        # * Initialize soloSoft (step 2)
        step2_hso_filename = os.path.join(directory_path, f"plate{k}_step2.hso")
        step2_hso_filename_list.append(step2_hso_filename)
        soloSoft = SoloSoft(
            filename=step2_hso_filename,
            plateList=[
                "DeepBlock.96.VWR-75870-792.sterile",
                "Empty",
                "TipBox.180uL.Axygen-EVF-180-R-S.bluebox",
                "Plate.96.Corning-3635.ClearUVAssay",
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

        # TODO: combine this with loop above
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

        """
        STEP 3: ADD ANTIBIOTIC TO CULTURE PLATES -------------------------------------------------------------------------------------
        """
        # * Initialize soloSoft (step 3)
        step3_hso_filename = os.path.join(directory_path, f"plate{k}_step3.hso")
        step3_hso_filename_list.append(step3_hso_filename)
        soloSoft = SoloSoft(
            filename=step3_hso_filename,
            plateList=[
                "DeepBlock.96.VWR-75870-792.sterile",
                "Empty",
                "TipBox.180uL.Axygen-EVF-180-R-S.bluebox",
                "Plate.96.Corning-3635.ClearUVAssay",
                "DeepBlock.96.VWR-75870-792.sterile",
                "DeepBlock.96.VWR-75870-792.sterile",
                "DeepBlock.96.VWR-75870-792.sterile",
                "DeepBlock.96.VWR-75870-792.sterile",
            ],
        )

        soloSoft.getTip("Position3")  
        for i in range(6, 0, -1):  # first half of plate
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
                dispense_volumes=Plate_96_Corning_3635_ClearUVAssay().setColumn(
                    i, antibiotic_transfer_volume_s3
                ),
                mix_at_finish=True,
                mix_cycles=num_mixes,
                mix_volume=destination_mix_volume_s3,
                aspirate_height=flat_bottom_z_shift,
                dispense_shift=[0, 0, flat_bottom_z_shift],
            )

        soloSoft.getTip("Position3")
        for i in range(6, 0, -1):  # second half of plate
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
                dispense_volumes=Plate_96_Corning_3635_ClearUVAssay().setColumn(
                    i + 6, antibiotic_transfer_volume_s3
                ),
                mix_at_finish=True,
                mix_cycles=num_mixes,
                mix_volume=destination_mix_volume_s3,
                aspirate_height=flat_bottom_z_shift,
                dispense_shift=[0, 0, flat_bottom_z_shift],
            )

        soloSoft.shuckTip()
        soloSoft.savePipeline()
    #* END LOOP

    """
    ADD ALL STEPS TO SOFTLINX PROTOCOL AND SEND TO HUDSON01 -----------------------------------------------------------------------
    """
    # initialize softLinx
    softLinx = SoftLinx("Steps_1_2_3", os.path.join(directory_path, "steps_1_2_3.slvp"))

    # define starting plate layout
    # softLinx.setPlates(
    #     {"SoftLinx.PlateCrane.Stack5": "Plate.96.Corning-3635.ClearUVAssay", 
    #     "SoftLinx.PlateCrane.Stack4": "TipBox.180uL.Axygen-EVF-180-R-S.bluebox"}
    # )
    softLinx.setPlates(
        {"SoftLinx.PlateCrane.Stack5": "Plate.96.Corning-3635.ClearUVAssay"}
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
        
        # replace tip box if necessary 
        if (k%2 == 0):
            # if k == 0: 
            #     replace_tip_box(softLinx, "Position3") 
            # else: 
            #     remove_tip_box(softLinx, "Position3")
            #     replace_tip_box(softLinx, "Position3")
            softLinx.soloSoftResetTipCount(3)  # reset the tip count at pos 3 not pos 1

        softLinx.plateCraneMoveCrane("SoftLinx.PlateCrane.Safe")

        # run all three liquid handling steps 
        softLinx.soloSoftRun(
            "C:\\labautomation\\instructions\\"
            + directory_name
            + "\\"
            + os.path.basename(step1_hso_filename_list[k])
        )
        softLinx.soloSoftRun(
            "C:\\labautomation\\instructions\\"
            + directory_name
            + "\\"
            + os.path.basename(step2_hso_filename_list[k])
        )
        softLinx.soloSoftRun(
            "C:\\labautomation\\instructions\\"
            + directory_name
            + "\\"
            + os.path.basename(step3_hso_filename_list[k])
        )

        # # Timepoint 0 Hidex reading (NOT NECESSARY)
        # softLinx.plateCraneMovePlate(
        #     ["SoftLinx.Solo.Position4"], ["SoftLinx.Hidex.Nest"]
        # )  # no need to open hidex
        # softLinx.hidexClose()
        # softLinx.plateCraneMoveCrane("SoftLinx.PlateCrane.Safe")
        # softLinx.hidexRun("Campaign1_noIncubate2")  # Hidex will close automatically

        # # Transfer Hidex data (timepoint 0 data)
        # softLinx.runProgram(
        #     "C:\\Users\\svcaibio\\Dev\\liquidhandling\\zeromq\\utils\\send_data.bat", arguments=k
        # )

        # Transfer plate to Liconic.Nest and replace lid
        #softLinx.plateCraneMovePlate(["SoftLinx.Hidex.Nest"], ["SoftLinx.Liconic.Nest"])
        softLinx.plateCraneMovePlate(["SoftLinx.Solo.Position4"], ["SoftLinx.Liconic.Nest"])
        #softLinx.hidexClose()
        softLinx.plateCraneReplaceLid(["SoftLinx.PlateCrane.LidNest2"], ["SoftLinx.Liconic.Nest"])
        softLinx.plateCraneMoveCrane("SoftLinx.PlateCrane.Safe")

        # Load plate into incubator
        softLinx.liconicLoadIncubator(loadID=k, holdWithoutIncubationTime=True)  
    #* END LOOP

    # reduce Hidex temp to reduce strain on instument over incubation (necessary?)
    softLinx.hidexRun("SetTemp20") 
    
    softLinx.liconicShake(shaker1Speed=30, shakeTime=[0,7,6,0]) # 7hrs 6 min

    # preheat Hidex for readings after incubation
    softLinx.hidexRun("SetTempWait37")  

    #* LOOP: unload plates from incubator and take endpoing reading
    for k in range(len(treatment)): 
        softLinx.liconicUnloadIncubator(loadID=k)
        softLinx.plateCraneRemoveLid(["SoftLinx.Liconic.Nest"], ["SoftLinx.PlateCrane.LidNest2"])
        softLinx.plateCraneMovePlate(["SoftLinx.Liconic.Nest"], ["SoftLinx.Hidex.Nest"])
        softLinx.hidexClose()
        softLinx.plateCraneMoveCrane("SoftLinx.PlateCrane.Safe")
        softLinx.hidexRun("Campaign1_noIncubate2")

        # transfer data to lambda6
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

    return return_val


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

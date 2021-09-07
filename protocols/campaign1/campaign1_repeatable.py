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


def generate_campaign1_repeatable(
    treatment,
    predicted_IC50=None,
    culture_column=None,
    media_start_column=None,
    treatment_dil_half=None,
):

    return_val = "PASS"

    # TODO: add constraints to media start column user input
    media_start_column = (
        media_start_column if media_start_column else 1
    )  # media column default = 1
    treatment_dil_half = (
        treatment_dil_half if treatment_dil_half else 1
    )  # treatment dilution half default = 1 (first half)

    # * Program variables
    blowoff_volume = 10
    num_mixes = 3
    # current_media_reservoir_volume = media_reservoir_volume = 7000
    media_z_shift = 0.5
    reservoir_z_shift = 0.5  # z shift for deep blocks (Deck Positions 3 and 5)
    flat_bottom_z_shift = 2  # Note: 1 is not high enough (tested)
    lambda6_path = "/lambda_stor/data/hudson/instructions/"

    # Step 1 variables
    culture_plate_column_num = (
        culture_column if culture_column else 1
    )  # Changed to column 1 for test on 07/14/21
    media_transfer_volume_s1 = 60
    culture_transfer_volume_s1 = 30
    # dilution_media_volume = 198
    half_dilution_media_volume = 99
    dilution_culture_volume = 22
    culture_plate_mix_volume_s1 = (
        100  # mix volume increased for test 09/07/21
    )
    culture_plate_num_mix = 10
    growth_plate_mix_volume_s1 = 40  
    culture_dilution_mix_volume = 150


    # Step 2 variables
    media_transfer_volume_s2 = (
        108  # two times = 216 uL (will add 24 uL antibiotic for 1:10 dilution)
    )
    last_column_transfer_volume_s2 = (
        120  # two times = 240uL (to equal volume in 1:10 dilution wells)
    )
    serial_antibiotic_transfer_volume_s2 = 24
    serial_source_mixing_volume_s2 = 20
    serial_source_num_mixes_s2 = 5
    serial_destination_mixing_volume_s2 = 100

    # Step 3 variables
    antibiotic_transfer_volume_s3 = 90
    antibiotic_mix_volume_s3 = 90
    destination_mix_volume_s3 = 100

    # * Get location of treatment
    try:
        treatment_plate_loc, treatment_column = find_treatment_loc(treatment)
    except Error as e:
        print(f"Unable to locate treatment {treatment}")
        raise  # need to know locaton of treatment, rest of protocol useless if not specified

    # * TODO: handle predicted IC50

    # * Create folder to store all instruction files
    project = "Campaign1"
    project_desc = "col" + str(culture_plate_column_num)
    version_num = "v1"
    timestamp = str(time.time()).split(".")[0]
    directory_name = f"{project}-{project_desc}-{version_num}-{timestamp}"
    directory_path = os.path.join(
        os.path.realpath(os.path.dirname(lambda6_path)), directory_name
    )
    print(f"Protocol directory created: {directory_path}")

    # * create new directory to hold new instructions
    try:
        os.makedirs(directory_path, exist_ok=True)
    except OSError as e:
        print(e)
        print(f"failed to create new directory for instructions: {directory_path}")

    """
    STEP 1: INNOCULATE GROWTH PLATE FROM SOURCE BACTERIA PLATE -----------------------------------------------------------------
    """
    # * Initialize soloSoft (step 1)
    step1_hso_filename = os.path.join(directory_path, "step_1.hso")
    soloSoft = SoloSoft(
        filename=step1_hso_filename,
        plateList=[
            "TipBox.180uL.Axygen-EVF-180-R-S.bluebox",
            "Empty",
            "DeepBlock.96.VWR-75870-792.sterile",
            "Plate.96.Corning-3635.ClearUVAssay",
            "DeepBlock.96.VWR-75870-792.sterile",
            "Plate.96.Corning-3635.ClearUVAssay",
            "DeepBlock.96.VWR-75870-792.sterile",
            "Plate.96.Corning-3635.ClearUVAssay",
        ],
    )

    # * Fill all columns of empty 96 well plate (corning 3383 or Falcon - ref 353916) with fresh lb media (12 channel in Position 3, media_start_column and media_start_column+1)
    soloSoft.getTip()
    j = 1
    for i in range(1, 7):  # first half plate = media from column 1
        soloSoft.aspirate(
            position="Position3",
            aspirate_volumes=Reservoir_12col_Agilent_201256_100_BATSgroup().setColumn(
                media_start_column, media_transfer_volume_s1
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
            position="Position3",
            aspirate_volumes=Reservoir_12col_Agilent_201256_100_BATSgroup().setColumn(
                media_start_column + 1, media_transfer_volume_s1
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
            position="Position3",
            aspirate_volumes=Reservoir_12col_Agilent_201256_100_BATSgroup().setColumn(
                media_start_column, half_dilution_media_volume
            ),
            aspirate_shift=[0, 0, media_z_shift],
        )
        soloSoft.dispense(
            position="Position7",
            dispense_volumes=Reservoir_12col_Agilent_201256_100_BATSgroup().setColumn(
                culture_plate_column_num, half_dilution_media_volume
            ),
            dispense_shift=[0, 0, reservoir_z_shift],
        )

    for i in range(
        2
    ):  # # from second media column -> cell dilution plate, column = same as culture column
        soloSoft.aspirate(
            position="Position3",
            aspirate_volumes=Reservoir_12col_Agilent_201256_100_BATSgroup().setColumn(
                media_start_column + 1, half_dilution_media_volume
            ),
            aspirate_shift=[0, 0, media_z_shift],
        )
        soloSoft.dispense(
            position="Position7",
            dispense_volumes=Reservoir_12col_Agilent_201256_100_BATSgroup().setColumn(
                culture_plate_column_num, half_dilution_media_volume
            ),
            dispense_shift=[0, 0, reservoir_z_shift],
        )

    # * Make culture 10 fold dilution 
    for i in range(1, 3):  # all cells dispensed into same cell dilution column
        soloSoft.aspirate(
            position="Position5",
            aspirate_volumes=DeepBlock_96VWR_75870_792_sterile().setColumn(
                culture_plate_column_num, dilution_culture_volume
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
                culture_plate_column_num, dilution_culture_volume
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
            culture_dilution_mix_volume, dilution_culture_volume
        ),
        aspirate_shift=[0,0,reservoir_z_shift],
        syringe_speed=25,
    )
    soloSoft.dispense(
        position="Position7",
        dispense_volumes=Reservoir_12col_Agilent_201256_100_BATSgroup().setColumn(
            culture_plate_column_num, dilution_culture_volume
        ),
        dispense_shift=[0, 0, reservoir_z_shift],
        mix_at_finish=True,
        mix_cycles=culture_plate_num_mix,
        mix_volume=culture_dilution_mix_volume,
        aspirate_height=reservoir_z_shift,
        syringe_speed=25,
        # blowoff=blowoff_volume,
    )

    # * Add bacteria from 10 fold diluted culture plate (Position 7, column = culture_plate_column_num) to growth plate with fresh media (both halves)
    
    for i in range(1,7): # trying a different method of cell dispensing (09/07/21)
        soloSoft.aspirate(     # well in first half
            position="Position7",
            aspirate_volumes=Reservoir_12col_Agilent_201256_100_BATSgroup().setColumn(
                culture_plate_column_num, culture_transfer_volume_s1
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

        soloSoft.aspirate(     # well in second half
            position="Position7",
            aspirate_volumes=Reservoir_12col_Agilent_201256_100_BATSgroup().setColumn(
                culture_plate_column_num, culture_transfer_volume_s1
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
                6+i, culture_transfer_volume_s1
            ),
            mix_at_finish=True,
            mix_cycles=num_mixes,
            mix_volume=growth_plate_mix_volume_s1,
            aspirate_height=flat_bottom_z_shift,
            dispense_shift=[0, 0, flat_bottom_z_shift],
            syringe_speed=25,
        )


    # OLD CELL TRANSFER METHODS 
    # for i in range(1, 7):  # first half growth plate
    #     soloSoft.aspirate(  # already mixed the cells, no need to do it before every transfer
    #         position="Position7",
    #         aspirate_volumes=Reservoir_12col_Agilent_201256_100_BATSgroup().setColumn(
    #             culture_plate_column_num, culture_transfer_volume_s1
    #         ),
    #         aspirate_shift=[
    #             0,
    #             0,
    #             reservoir_z_shift,
    #         ],
    #         syringe_speed=25,
    #     )
    #     soloSoft.dispense(  # do need to mix at end of transfer
    #         position="Position4",
    #         dispense_volumes=Plate_96_Corning_3635_ClearUVAssay().setColumn(
    #             i, culture_transfer_volume_s1
    #         ),
    #         mix_at_finish=True,
    #         mix_cycles=num_mixes,
    #         mix_volume=growth_plate_mix_volume_s1,
    #         aspirate_height=flat_bottom_z_shift,
    #         dispense_shift=[0, 0, flat_bottom_z_shift],
    #         syringe_speed=25,
    #     )

    # for i in range(7, 13):  # second half growth plate
    #     soloSoft.aspirate(  # already mixed the cells, no need to do it before every transfer
    #         position="Position7",
    #         aspirate_volumes=Reservoir_12col_Agilent_201256_100_BATSgroup().setColumn(
    #             culture_plate_column_num, culture_transfer_volume_s1
    #         ),
    #         aspirate_shift=[0, 0, reservoir_z_shift],
    #         syringe_speed=25,
    #     )
    #     soloSoft.dispense(  # do need to mix at end of transfer
    #         position="Position4",
    #         dispense_volumes=Plate_96_Corning_3635_ClearUVAssay().setColumn(
    #             i, culture_transfer_volume_s1
    #         ),
    #         mix_at_finish=True,
    #         mix_cycles=num_mixes,
    #         mix_volume=growth_plate_mix_volume_s1,
    #         aspirate_height=flat_bottom_z_shift,
    #         dispense_shift=[0, 0, flat_bottom_z_shift],
    #         syringe_speed=25,
    #     )

    soloSoft.shuckTip()
    soloSoft.savePipeline()

    """
    STEP 2: PERFORM SERIAL DILUTIONS ON TREATMENT -------------------------------------------------------------------------------
    """
    # * Initialize soloSoft (step 2)
    step2_hso_filename = os.path.join(directory_path, "step_2.hso")
    soloSoft = SoloSoft(
        filename=step2_hso_filename,
        plateList=[
            "TipBox.180uL.Axygen-EVF-180-R-S.bluebox",
            "Empty",
            "DeepBlock.96.VWR-75870-792.sterile",
            "Plate.96.Corning-3635.ClearUVAssay",
            "DeepBlock.96.VWR-75870-792.sterile",
            "Plate.96.Corning-3635.ClearUVAssay",
            "DeepBlock.96.VWR-75870-792.sterile",
            "Plate.96.Corning-3635.ClearUVAssay",
        ],
    )

    # * Fill colums 1-5 of generic 96 well plate with 216uL lb media in two steps (will use for both halves of plate)
    soloSoft.getTip()
    for i in range(
        (6 * (treatment_dil_half - 1)) + 1, (6 * (treatment_dil_half - 1)) + 6
    ):  # columns 1-5 or columns 7-11 (treatment_dil_half = 1 or 2)
        # draws from both lb media wells to prevent running out of media -> TODO: volume management
        soloSoft.aspirate(  # first lb media well
            position="Position3",
            aspirate_volumes=Reservoir_12col_Agilent_201256_100_BATSgroup().setColumn(
                media_start_column, media_transfer_volume_s2
            ),
            aspirate_shift=[0, 0, media_z_shift],
            # pre_aspirate=blowoff_volume,
        )
        soloSoft.dispense(
            position="Position6",
            dispense_volumes=Plate_96_Corning_3635_ClearUVAssay().setColumn(
                i, media_transfer_volume_s2
            ),
            dispense_shift=[0, 0, flat_bottom_z_shift],
            # blowoff=blowoff_volume,
        )

        soloSoft.aspirate(  # second lb media well
            position="Position3",
            aspirate_volumes=Reservoir_12col_Agilent_201256_100_BATSgroup().setColumn(
                media_start_column + 1, media_transfer_volume_s2
            ),
            aspirate_shift=[0, 0, media_z_shift],
            # pre_aspirate=blowoff_volume,
        )
        soloSoft.dispense(
            position="Position6",
            dispense_volumes=Plate_96_Corning_3635_ClearUVAssay().setColumn(
                i, media_transfer_volume_s2
            ),
            dispense_shift=[0, 0, flat_bottom_z_shift],
            # blowoff=blowoff_volume,
        )

    # * Fill column 6 of a generic 96 well plate with 240uL lb media in two steps
    for i in range(media_start_column, media_start_column + 2):
        soloSoft.aspirate(  # first lb media well
            position="Position3",
            aspirate_volumes=Reservoir_12col_Agilent_201256_100_BATSgroup().setColumn(
                i, last_column_transfer_volume_s2
            ),
            aspirate_shift=[0, 0, media_z_shift],
            # pre_aspirate=blowoff_volume,
        )
        soloSoft.dispense(
            position="Position6",
            dispense_volumes=Plate_96_Corning_3635_ClearUVAssay().setColumn(
                (6 * (treatment_dil_half - 1)) + 6, last_column_transfer_volume_s2
            ),
            dispense_shift=[0, 0, flat_bottom_z_shift],
            # blowoff=blowoff_volume,
        )

    # * Transfer treatment in to first column of treatement dilution plate (will make 1:10 dilution)
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
        dispense_volumes=Plate_96_Corning_3635_ClearUVAssay().setColumn(
            (6 * (treatment_dil_half - 1)) + 1, serial_antibiotic_transfer_volume_s2
        ),
        dispense_shift=[0, 0, flat_bottom_z_shift],
        blowoff=blowoff_volume,
        # mix_at_finish=True,
        # mix_cycles=num_mixes,
        # mix_volume=serial_destination_mixing_volume_s2,
        aspirate_height=flat_bottom_z_shift,
    )

    # * Serial dilution within Generic 96 well plate (Corning or Falcon) - mix 3 times before and after transfer
    for i in range(
        (6 * (treatment_dil_half - 1)) + 1, (6 * (treatment_dil_half - 1)) + 5
    ):  # don't serial dilute into the last column (control column)
        # if i == 4:  # switch tips half way through to reduce error   #TODO: Test if you need this
        #     soloSoft.getTip()
        soloSoft.aspirate(
            position="Position6",
            aspirate_volumes=Plate_96_Corning_3635_ClearUVAssay().setColumn(
                i, serial_antibiotic_transfer_volume_s2
            ),
            aspirate_shift=[0, 0, flat_bottom_z_shift],
            pre_aspirate=blowoff_volume,
            mix_at_start=True,
            mix_cycles=num_mixes,
            mix_volume=serial_destination_mixing_volume_s2,
            dispense_height=flat_bottom_z_shift,
        )
        soloSoft.dispense(
            position="Position6",
            dispense_volumes=Plate_96_Corning_3635_ClearUVAssay().setColumn(
                i + 1, serial_antibiotic_transfer_volume_s2
            ),
            dispense_shift=[0, 0, flat_bottom_z_shift],
            blowoff=blowoff_volume,
            mix_at_finish=True,
            mix_cycles=num_mixes,
            mix_volume=serial_destination_mixing_volume_s2,
            aspirate_height=flat_bottom_z_shift,
        )
    # no need to throw away excess volume from last column of serial dilution

    soloSoft.shuckTip()
    soloSoft.savePipeline()

    """
    STEP 3: ADD ANTIBIOTIC TO CULTURE PLATES -------------------------------------------------------------------------------------
    """
    # * Initialize soloSoft (step 3)
    step3_hso_filename = os.path.join(directory_path, "step_3.hso")
    soloSoft = SoloSoft(
        filename=step3_hso_filename,
        plateList=[
            "TipBox.180uL.Axygen-EVF-180-R-S.bluebox",
            "Empty",
            "DeepBlock.96.VWR-75870-792.sterile",
            "Plate.96.Corning-3635.ClearUVAssay",
            "DeepBlock.96.VWR-75870-792.sterile",
            "Plate.96.Corning-3635.ClearUVAssay",
            "DeepBlock.96.VWR-75870-792.sterile",
            "Plate.96.Corning-3635.ClearUVAssay",
        ],
    )

    soloSoft.getTip()
    for i in range(6, 0, -1):  # first half of plate
        if i == 3:  # switch tips half way through to reduce error
            soloSoft.getTip()
        soloSoft.aspirate(
            position="Position6",
            aspirate_volumes=Plate_96_Corning_3635_ClearUVAssay().setColumn(
                (6 * (treatment_dil_half - 1)) + i, antibiotic_transfer_volume_s3
            ),
            mix_at_start=True,
            mix_cycles=num_mixes,
            mix_volume=antibiotic_mix_volume_s3,
            dispense_height=flat_bottom_z_shift,
            aspirate_shift=[0, 0, flat_bottom_z_shift],
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

    soloSoft.getTip()
    for i in range(6, 0, -1):  # second half of plate
        if i == 3:  # switch tips half way through to reduce error
            soloSoft.getTip()
        soloSoft.aspirate(
            position="Position6",
            aspirate_volumes=Plate_96_Corning_3635_ClearUVAssay().setColumn(
                (6 * (treatment_dil_half - 1)) + i, antibiotic_transfer_volume_s3
            ),
            mix_at_start=True,
            mix_cycles=num_mixes,
            mix_volume=antibiotic_mix_volume_s3,
            dispense_height=flat_bottom_z_shift,
            aspirate_shift=[0, 0, flat_bottom_z_shift],
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

    """
    ADD ALL STEPS TO SOFTLINX PROTOCOL AND SEND TO HUDSON01 -----------------------------------------------------------------------
    """
    # initialize softLinx
    softLinx = SoftLinx("Steps_1_2_3", os.path.join(directory_path, "steps_1_2_3.slvp"))

    # define starting plate layout
    softLinx.setPlates(
        {"SoftLinx.PlateCrane.Stack5": "Plate.96.Corning-3635.ClearUVAssay"}
    )

    # restock growth assay plate before run
    softLinx.plateCraneMovePlate(
        ["SoftLinx.PlateCrane.Stack5"], ["SoftLinx.Solo.Position4"]
    )
    # remove lid and place in Lid Nest
    softLinx.plateCraneRemoveLid(
        ["SoftLinx.Solo.Position4"], ["SoftLinx.PlateCrane.LidNest2"]
    )
    softLinx.plateCraneMoveCrane("SoftLinx.PlateCrane.Safe")

    # run all three liquid handling steps (with paths to .hso files on hudson01)
    softLinx.soloSoftResetTipCount(1)  # SoloSoft will reset to full tip box before run
    softLinx.soloSoftRun(
        "C:\\labautomation\\instructions\\"
        + directory_name
        + "\\"
        + os.path.basename(step1_hso_filename)
    )
    softLinx.soloSoftRun(
        "C:\\labautomation\\instructions\\"
        + directory_name
        + "\\"
        + os.path.basename(step2_hso_filename)
    )
    softLinx.soloSoftRun(
        "C:\\labautomation\\instructions\\"
        + directory_name
        + "\\"
        + os.path.basename(step3_hso_filename)
    )

    # DON'T DO THIS IFINCUBATING ONE PLATE IN HIDEX
    # #replace the lid
    # softLinx.plateCraneReplaceLid(["SoftLinx.PlateCrane.LidNest2"], ["SoftLinx.Solo.Position4"])

    # move growth plate to Temp deck (This is where the plate would be moved to the incubator)
    # softLinx.plateCraneMovePlate(
    #     ["SoftLinx.Solo.Position4"], ["SoftLinx.PlateCrane.LidNest1"]
    # )  # no need to open hidex
    softLinx.plateCraneMovePlate(
        ["SoftLinx.Solo.Position4"], ["SoftLinx.Hidex.Nest"]
    )  # no need to open hidex
    softLinx.hidexClose()
    softLinx.plateCraneMoveCrane("SoftLinx.PlateCrane.Safe")

    # Run Hidex Protocol (this will close the Hidex)
    softLinx.hidexRun("Campaign1")  # full 16 hour Hidex incubation

    # Transfer Hidex data from C:\labautomation\data to compute cell (lambda6)
    softLinx.runProgram(
        "C:\\Users\\svcaibio\\Dev\\liquidhandling\\zeromq\\utils\\send_data.bat"
    )

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
            ],
            start_new_session=True,
        ).pid
        print("New instruction directory passed to lambda6_send_message.py")
    except Error as e:
        print(e)
        print("Could not send new instructions to hudson01")

    return return_val


def find_treatment_loc(treatment_name):  # TODO: Move this method out of protocol file
    """
    Connect to SQL database. Determine plate # and well location of desired treatment
    (for now, these locations will be hardcoded (plate assumed to be on Solo deck))

    """
    # {treatment_name: [Plate location, column number], ... }
    # treatment_locations = {"KAN": ["Position3", 3], "peptide1": ["Position3", 3]}
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
    )
    parser.add_argument(
        "-cc",
        "--culture_column",
        help="culture plate column to use, must be an integer (ex. 3 means column 3)",
        required=False,
        type=int,
    )
    parser.add_argument(
        "-mc",
        "--media_start_column",
        help="media plate column to start with, must be an integer (ex. 1) Will use column specified(i) and column(i+1). (ex. -mc 1 = first and second column)",
        required=False,
        type=int,
    )
    parser.add_argument(
        "-tdh",
        "--treatment_dilution_half",
        help="which half of the treatment serial dilution plate to use, must be an integer (1 or 2). 1 = columns 1-6, 2 = columns 7-12",
        required=False,
        type=int,
    )
    args = vars(parser.parse_args())
    print(
        "treatment = {}, IC50 = {}, culture_column = {}".format(
            args["treatment"],
            args["predicted_IC50"],
            args["culture_column"],
            args["media_start_column"],
            args["treatment_dilution_half"],
        )
    )

    # pass to method
    generate_campaign1_repeatable(
        args["treatment"],
        args["predicted_IC50"],
        args["culture_column"],
        args["media_start_column"],
        args["treatment_dilution_half"],
    )


if __name__ == "__main__":
    # execute only if run as a script
    main(sys.argv)

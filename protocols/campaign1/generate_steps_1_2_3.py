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


def generate_steps_1_2_3(treatment, predicted_IC50=None):

    return_val = "PASS"

    # * Program variables
    blowoff_volume = 10
    num_mixes = 3
    current_media_reservoir_volume = media_reservoir_volume = 7000
    reservoir_z_shift = 0.5  # z shift for deep blocks (Deck Positions 3 and 5)
    lambda6_path = "/lambda_stor/data/hudson/instructions/"

    # Step 1 variables
    culture_plate_column_num = 1  # Changed to column 1 for test on 07/14/21
    media_transfer_volume_s1 = 60
    culture_transfer_volume_s1 = 30
    # dilution_media_volume = 198
    half_dilution_media_volume = 99
    dilution_culture_volume = 22
    culture_plate_mix_volume_s1 = (
        30  # best to mix with same volume transferred, ok for min volume
    )
    growth_plate_mix_volume_s1 = 40

    # Step 2 variables
    media_transfer_volume_s2 = (
        108  # two times = 216 uL (will add 24 uL antibiotic for 1:10 dilution)
    )
    first_column_transfer_volume_s2 = (
        120  # two times = 240uL (to equal volume in 1:10 dilution wells)
    )
    serial_antibiotic_transfer_volume_s2 = 24
    serial_source_mixing_volume_s2 = 80
    serial_source_num_mixes_s2 = 8
    serial_destination_mixing_volume_s2 = 100

    # Step 3 variables
    antibiotic_transfer_volume_s3 = 90
    antibiotic_mix_volume_s3 = 90
    destination_mix_volume_s3 = 100

    # * Get location of treatment
    try:
        treatment_plate_loc, treatment_column = find_treatment_loc(treatment)
    except Error as e:
        print(f"Unale to locate treatment {treatment}")
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
            "Plate.96.Corning-3635.ClearUVAssay",
            "Empty",
        ],
    )

    # * Fill all columns of empty 96 well plate (corning 3383 or Falcon - ref 353916) with fresh lb media (12 channel in Position 3, column 1)
    soloSoft.getTip()
    j = 1
    for i in range(1, 7):  # first half plate = media from column 1
        soloSoft.aspirate(
            position="Position3",
            aspirate_volumes=Reservoir_12col_Agilent_201256_100_BATSgroup().setColumn(
                1, media_transfer_volume_s1
            ),
            aspirate_shift=[0, 0, reservoir_z_shift],
        )
        soloSoft.dispense(
            position="Position4",
            dispense_volumes=Plate_96_Corning_3635_ClearUVAssay().setColumn(
                i, media_transfer_volume_s1
            ),
            dispense_shift=[0, 0, 2],
        )

    for i in range(7, 13):  # second half plate = media from column 2
        soloSoft.aspirate(
            position="Position3",
            aspirate_volumes=Reservoir_12col_Agilent_201256_100_BATSgroup().setColumn(
                2, media_transfer_volume_s1
            ),
            aspirate_shift=[0, 0, reservoir_z_shift],
        )
        soloSoft.dispense(
            position="Position4",
            dispense_volumes=Plate_96_Corning_3635_ClearUVAssay().setColumn(
                i, media_transfer_volume_s1
            ),
            dispense_shift=[0, 0, 2],
        )

    # * Fill first two columns of culture 10 fold dilution plate with fresh lb media (do in two steps due to 180uL filter tips)
    for i in range(2):  # first column
        soloSoft.aspirate(
            position="Position3",
            aspirate_volumes=Reservoir_12col_Agilent_201256_100_BATSgroup().setColumn(
                1, half_dilution_media_volume
            ),
            aspirate_shift=[0, 0, reservoir_z_shift],
        )
        soloSoft.dispense(
            position="Position7",
            dispense_volumes=Plate_96_Corning_3635_ClearUVAssay().setColumn(
                1, half_dilution_media_volume
            ),
            dispense_shift=[0, 0, 2],
        )

    for i in range(2):  # second column
        soloSoft.aspirate(
            position="Position3",
            aspirate_volumes=Reservoir_12col_Agilent_201256_100_BATSgroup().setColumn(
                2, half_dilution_media_volume
            ),
            aspirate_shift=[0, 0, reservoir_z_shift],
        )
        soloSoft.dispense(
            position="Position7",
            dispense_volumes=Plate_96_Corning_3635_ClearUVAssay().setColumn(
                2, half_dilution_media_volume
            ),
            dispense_shift=[0, 0, 2],
        )

    # * Make culture 10 fold dilution (one column for each half of plate)
    for i in range(1, 3):
        soloSoft.aspirate(
            position="Position5",
            aspirate_volumes=DeepBlock_96VWR_75870_792_sterile().setColumn(
                culture_plate_column_num, dilution_culture_volume
            ),
            aspirate_shift=[0, 0, 2],
            mix_at_start=True,
            mix_cycles=num_mixes,
            mix_volume=culture_plate_mix_volume_s1,
            dispense_height=2,
            # pre_aspirate=blowoff_volume,
            syringe_speed=25,
        )
        soloSoft.dispense(
            position="Position7",
            dispense_volumes=Plate_96_Corning_3635_ClearUVAssay().setColumn(
                i, dilution_culture_volume
            ),
            dispense_shift=[0, 0, 2],
            mix_at_finish=True,
            mix_cycles=num_mixes,
            mix_volume=culture_plate_mix_volume_s1,
            aspirate_height=2,
            syringe_speed=25,
            # blowoff=blowoff_volume,
        )

    # * Add bacteria from 10 fold diluted culture plate (Position 7, column 1 and 2) to growth plate with fresh media (both halves)
    for i in range(1, 7):  # first half growth plate
        soloSoft.aspirate(  # already mixed the cells, no need to do it before every transfer
            position="Position7",
            aspirate_volumes=Plate_96_Corning_3635_ClearUVAssay().setColumn(
                1, culture_transfer_volume_s1
            ),
            aspirate_shift=[
                0,
                0,
                2,
            ],  # prevents 50 uL tips from going too deep in 96 deep well plate
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
            aspirate_height=2,
            dispense_shift=[0, 0, 2],
            syringe_speed=25,
        )

    for i in range(7, 13):  # second half growth plate
        soloSoft.aspirate(  # already mixed the cells, no need to do it before every transfer
            position="Position7",
            aspirate_volumes=Plate_96_Corning_3635_ClearUVAssay().setColumn(
                2, culture_transfer_volume_s1
            ),
            aspirate_shift=[
                0,
                0,
                2,
            ],  # prevents 50 uL tips from going too deep in 96 deep well plate
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
            aspirate_height=2,
            dispense_shift=[0, 0, 2],
            syringe_speed=25,
        )

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
            "Plate.96.Corning-3635.ClearUVAssay",
            "Empty",
        ],
    )

    # * Fill colums 2-6 of generic 96 well plate with lb media (will use for both halves of plate)
    soloSoft.getTip()
    for i in range(2, 7):
        # draws from both lb media wells to prevent running out of media -> TODO: volume management
        soloSoft.aspirate(  # first lb media well
            position="Position3",
            aspirate_volumes=Reservoir_12col_Agilent_201256_100_BATSgroup().setColumn(
                1, media_transfer_volume_s2
            ),
            aspirate_shift=[0, 0, reservoir_z_shift],
            # pre_aspirate=blowoff_volume,
        )
        soloSoft.dispense(
            position="Position6",
            dispense_volumes=Plate_96_Corning_3635_ClearUVAssay().setColumn(
                i, media_transfer_volume_s2
            ),
            dispense_shift=[0, 0, 2],
            # blowoff=blowoff_volume,
        )

        soloSoft.aspirate(  # second lb media well
            position="Position3",
            aspirate_volumes=Reservoir_12col_Agilent_201256_100_BATSgroup().setColumn(
                2, media_transfer_volume_s2
            ),
            aspirate_shift=[0, 0, reservoir_z_shift],
            # pre_aspirate=blowoff_volume,
        )
        soloSoft.dispense(
            position="Position6",
            dispense_volumes=Plate_96_Corning_3635_ClearUVAssay().setColumn(
                i, media_transfer_volume_s2
            ),
            dispense_shift=[0, 0, 2],
            # blowoff=blowoff_volume,
        )

    # * Transfer undiluted treatment stock solution (12 channel in Position 3, 3rd row) into empty first row of serial dilution plate
    for i in range(2):
        soloSoft.aspirate(
            position=treatment_plate_loc,
            aspirate_volumes=Reservoir_12col_Agilent_201256_100_BATSgroup().setColumn(
                treatment_column, first_column_transfer_volume_s2
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
                1, first_column_transfer_volume_s2
            ),
            dispense_shift=[0, 0, 2],
            blowoff=blowoff_volume,
            # mix_at_finish=True,
            # mix_cycles=num_mixes,
            # mix_volume=serial_destination_mixing_volume_s2,
            aspirate_height=2,
        )

    # * Serial dilution within Generic 96 well plate (Corning or Falcon) - mix 5 times before and after transfer
    for i in range(1, 6):
        if i == 4:  # switch tips half way through to reduce error
            soloSoft.getTip()
        soloSoft.aspirate(
            position="Position6",
            aspirate_volumes=Plate_96_Corning_3635_ClearUVAssay().setColumn(
                i, serial_antibiotic_transfer_volume_s2
            ),
            aspirate_shift=[0, 0, 2],
            pre_aspirate=blowoff_volume,
            mix_at_start=True,
            mix_cycles=num_mixes,
            mix_volume=serial_destination_mixing_volume_s2,
            dispense_height=2,
        )
        soloSoft.dispense(
            position="Position6",
            dispense_volumes=Plate_96_Corning_3635_ClearUVAssay().setColumn(
                i + 1, serial_antibiotic_transfer_volume_s2
            ),
            dispense_shift=[0, 0, 2],
            blowoff=blowoff_volume,
            mix_at_finish=True,
            mix_cycles=num_mixes,
            mix_volume=serial_destination_mixing_volume_s2,
            aspirate_height=2,
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
            "Plate.96.Corning-3635.ClearUVAssay",
            "Empty",
        ],
    )

    soloSoft.getTip()
    for i in range(6, 0, -1):  # first half of plate
        if i == 3:  # switch tips half way through to reduce error
            soloSoft.getTip()
        soloSoft.aspirate(
            position="Position6",
            aspirate_volumes=Plate_96_Corning_3635_ClearUVAssay().setColumn(
                i, antibiotic_transfer_volume_s3
            ),
            mix_at_start=True,
            mix_cycles=num_mixes,
            mix_volume=antibiotic_mix_volume_s3,
            dispense_height=2,
            aspirate_shift=[0, 0, 2],
        )
        soloSoft.dispense(
            position="Position4",
            dispense_volumes=Plate_96_Corning_3635_ClearUVAssay().setColumn(
                i, antibiotic_transfer_volume_s3
            ),
            mix_at_finish=True,
            mix_cycles=num_mixes,
            mix_volume=destination_mix_volume_s3,
            aspirate_height=2,
            dispense_shift=[0, 0, 2],
        )

    soloSoft.getTip()
    for i in range(6, 0, -1):  # second half of plate
        if i == 3:  # switch tips half way through to reduce error
            soloSoft.getTip()
        soloSoft.aspirate(
            position="Position6",
            aspirate_volumes=Plate_96_Corning_3635_ClearUVAssay().setColumn(
                i, antibiotic_transfer_volume_s3
            ),
            mix_at_start=True,
            mix_cycles=num_mixes,
            mix_volume=antibiotic_mix_volume_s3,
            dispense_height=2,
            aspirate_shift=[0, 0, 2],
        )
        soloSoft.dispense(
            position="Position4",
            dispense_volumes=Plate_96_Corning_3635_ClearUVAssay().setColumn(
                i + 6, antibiotic_transfer_volume_s3
            ),
            mix_at_finish=True,
            mix_cycles=num_mixes,
            mix_volume=destination_mix_volume_s3,
            aspirate_height=2,
            dispense_shift=[0, 0, 2],
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

    # move growth plate to Hidex
    softLinx.plateCraneMovePlate(
        ["SoftLinx.Solo.Position4"], ["SoftLinx.Hidex.Nest"]
    )  # no need to open hidex
    softLinx.hidexClose()
    softLinx.plateCraneMoveCrane("SoftLinx.PlateCrane.Safe")

    # Run Hidex Protocol
    softLinx.hidexRun("Campaign1")

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
    treatment_locations = {"KAN": ["Position3", 3], "peptide1": ["Position3", 3]}

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
    args = vars(parser.parse_args())
    print("treatment = {}, IC50 = {}".format(args["treatment"], args["predicted_IC50"]))

    # pass to method
    generate_steps_1_2_3(args["treatment"], args["predicted_IC50"])


if __name__ == "__main__":
    # execute only if run as a script
    main(sys.argv)

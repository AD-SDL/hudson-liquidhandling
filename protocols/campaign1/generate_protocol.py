"""
CAMPAIGN 1, STEPS 1-3 -> GOAL: Run two iterations without human intervention

STEP 1: Innoculate growth plate from source bacteria plate 
STEP 2: Perform serial dilutions on antibiotic
    (see command line options below)
STEP 3: Add antibiotic to culture plates 

Command Line Options: (--start_cons AND/OR --end_cons)
    Usages:
    - "python generate_protocol.py"
        - runs the default version of this program. 
        - 6 columns -> first column is pure stock antibiotic solution and next 5 columns are serial 10 fold dilutions

    - "python generate_protocol.py --start_cons {starting consentration}" 
        - ex. python generate_protocol.py --start_cons 1/2000
        - 6 columns -> first column is diluted from stock antibiotic solution to match desired starting concentration 
            and next 5 columns are serial 10 fold dilutions
        
    - "python generate_protocol.py --start_cons {starting concentration} --end_cons {ending consentration}
        - ex. python generate_protocol.py --start_cons 1/2000 --end_cons 1/64000 
        - 6 columns -> first column is diluted from stock antibiotic solution to match desired starting concentration
            and next 5 columns are serial diluted evenly so that the final column contains the desired ending concentration

    - "python generate_protocol.py --end_cons {ending concentration}
        - ex. python generate_protocol.py --end_cons 1/32000
        - 6 columns -> first column is pute antibiotic stock solution because no starting concentration was entered in to the command line
            and next 5 columns are serial diluted evenly so that the final columb contains the desired ending concentration

Deck Layout: (ALL OPEN DECK POSITITIONS USED)
1 -> 200 uL Tips ("TipBox.200uL.Corning-4864.orangebox")
2 -> HEATING NEST
3 -> Lb media well, antibiotic stock solution well (12 channel reservoir) -> column 1 = lb media; column 2 = antibiotic stock solution 
4 -> Growth plate (Corning 3383 or Falcon - ref 353916)
5 -> Culture plate from freezer (96 deep well round bottom)
6 -> Antibiotic serial dilution plate (Corning 3383 or Falcon - ref 353916)
7 -> 10 fold culture plate dilution (Corning 3383 or Falcon - ref 353916)
8 -> 50 uL Tips("TipBox-50uL EV-50-R-S)  <- just in case very small volumes need to be transered in antibiotic serial dilution step

TODO: 
    - Implement volume management for the lb media (-> for two rounds it should be ok without it)
    
"""

import os
import sys
import argparse
from liquidhandling import SoloSoft
from liquidhandling import SoftLinx
from liquidhandling import ZAgilentReservoir_1row, NinetySixDeepWell, GenericPlate96Well

parser = argparse.ArgumentParser()
parser.add_argument(
    "--start_cons",
    help="generated the protocol with the specified starting concentration",
)
parser.add_argument(
    "--end_cons", help="generates the protocol with the specified enfing concentration"
)
args = parser.parse_args()

start_cons = None
end_cons = None

# * Format the command line input
# NOTE: The command line start/end cons specify final concentrations desured in Hidex growth plate.
# NOTE: Concentrations in the antibiotic serial dilution plate will be double the entered start/end cons to make this work correctly
if args.start_cons:
    start_cons_string = args.start_cons
    if "/" in start_cons_string:  # parse if start_cons entered as fraction
        start_numerator, start_denominator = (
            int((start_cons_string.split("/")[0].strip())),
            int(start_cons_string.split("/")[1].strip()),
        )
        start_cons = (
            float(start_numerator / start_denominator) * 2
        )  # DOUBLED for correct Hidex plate conc.
    else:
        start_cons = (
            float(start_cons_string.strip()) * 2
        )  # DOUBLED for correct Hidex plate conc.

if args.end_cons:
    end_cons_string = args.end_cons
    if "/" in end_cons_string:  # parse if end_cons entered as a fraction
        end_numerator, end_denominator = (
            int(end_cons_string.split("/")[0].strip()),
            int(end_cons_string.split("/")[1].strip()),
        )
        end_cons = (
            float(end_numerator / end_denominator) * 2
        )  # DOUBLED for correct Hidex plate conc.
    else:
        end_cons = (
            float(end_cons_string.strip()) * 2
        )  # DOUBLED for correct Hidex plate conc.

# * Program variables
blowoff_volume = 10
num_mixes = 5
current_media_reservoir_volume = media_reservoir_volume = 7000
num_columns = 6

# Step 1 variables
culture_plate_column_num = 2
media_transfer_volume_s1 = 60
culture_transfer_volume_s1 = 30
dilution_media_volume = 198
dilution_culture_volume = 22
culture_plate_mix_volume_s1 = 50
growth_plate_mix_volume_s1 = 40

# Step 2 variables
serial_source_num_mixes_s2 = 10
stock_cons = 1 / 1000  # following variables added for command line version of protocol
desired_volume_serial_dilution = 150
default_df = 1 / 10

# Step 3 variables
antibiotic_transfer_volume_s3 = 90
antibiotic_mix_volume_s3 = 90
destination_mix_volume_s3 = 120

# * Initialize and set deck layout (both 200uL and 50uL tips included)
soloSoft = SoloSoft(
    filename="generate_protocol.hso",
    plateList=[
        "TipBox.200uL.Corning-4864.orangebox",
        "Empty",
        "12 Channel Reservoir",
        "Corning 3383",
        "96 Deep Protein",
        "Corning 3383",
        "Corning 3383",
        "TipBox.50uL.Axygen-EV-50-R-S.tealbox",
    ],
)

"""
STEP 1: INNOCULATE GROWTH PLATE FROM SOURCE BACTERIA PLATE -----------------------------------------------------------------
"""
# * Fill 6 columns of empty 96 well plate (corning 3383 or Falcon - ref 353916) with fresh lb media (12 channel in Position 3, column 1)
soloSoft.getTip()
j = 1
for i in range(1, 7):
    soloSoft.aspirate(
        position="Position3",
        aspirate_volumes=ZAgilentReservoir_1row().setColumn(
            1, media_transfer_volume_s1
        ),
        aspirate_shift=[
            0,
            0,
            4,
        ],
    )
    soloSoft.dispense(
        position="Position4",
        dispense_volumes=GenericPlate96Well().setColumn(i, media_transfer_volume_s1),
        dispense_shift=[0, 0, 2],
    )

# * Fill first column of culture 10 fold dilution plate with fresh lb media
soloSoft.aspirate(
    position="Position3",
    aspirate_volumes=ZAgilentReservoir_1row().setColumn(1, dilution_media_volume),
    aspirate_shift=[0, 0, 4],
)
soloSoft.dispense(
    position="Position7",
    dispense_volumes=GenericPlate96Well().setColumn(1, dilution_media_volume),
    dispense_shift=[0, 0, 2],
)

# * Add bacteria from thawed culture plate (Position 5, column defined in variable) to dilution plate (Position 7, column 1) to make culture 10 fold dilution
soloSoft.aspirate(
    position="Position5",
    aspirate_volumes=NinetySixDeepWell().setColumn(
        culture_plate_column_num, dilution_culture_volume
    ),
    aspirate_shift=[0, 0, 2],
    mix_at_start=True,
    mix_cycles=num_mixes,
    mix_volume=culture_plate_mix_volume_s1,
    dispense_height=2,
    pre_aspirate=blowoff_volume,
    syringe_speed=25,
)
soloSoft.dispense(
    position="Position7",
    dispense_volumes=GenericPlate96Well().setColumn(1, dilution_culture_volume),
    dispense_shift=[0, 0, 2],
    mix_at_finish=True,
    mix_cycles=num_mixes,
    mix_volume=culture_plate_mix_volume_s1,
    aspirate_height=2,
    syringe_speed=25,
    blowoff=blowoff_volume,
)

# * Add bacteria from 10 fold diluted culture plate (Position 7, column 1) to growth plate with fresh media (columns 1-6)
for i in range(1, 7):
    soloSoft.aspirate(  # already mixed the cells, no need to do it before every transfer
        position="Position7",
        aspirate_volumes=GenericPlate96Well().setColumn(1, culture_transfer_volume_s1),
        aspirate_shift=[
            0,
            0,
            2,
        ],
        syringe_speed=25,
    )
    soloSoft.dispense(  # do need to mix at end of transfer
        position="Position4",
        dispense_volumes=GenericPlate96Well().setColumn(i, culture_transfer_volume_s1),
        mix_at_finish=True,
        mix_cycles=num_mixes,
        mix_volume=growth_plate_mix_volume_s1,
        aspirate_height=2,
        dispense_shift=[0, 0, 2],
        syringe_speed=25,
    )

"""
STEP 2: PERFORM SERIAL DILUTIONS ON ANTIBIOTIC -------------------------------------------------------------------------------
"""
# * TRANSFER VOLUME CALCULATIONS
first_column_df = 1.0  # default first column dilution factor => pure stock solution in first column, dilute from there
first_column_cons = stock_cons
df = default_df

# if --start_cons entered, calculate volumes needed to dilute to start_cons in first column
if args.start_cons:
    first_column_df = start_cons / stock_cons
    first_column_cons = start_cons

# if --end_cons entered, calculate dilution factor needed for final serial dilution to result in end_cons
if args.end_cons:
    df = (end_cons / first_column_cons) ** (1 / (num_columns - 1))

# calculate amounts to transfer into the first column
stock_transfer_first_column = int(first_column_df * desired_volume_serial_dilution)
diluent_transfer_first_column = int(
    desired_volume_serial_dilution - stock_transfer_first_column
)
print("ANTIBIOTIC SERIAL DILUTIONS")
print("Into column 1:")
print("\tStock trasfer volume: " + str(stock_transfer_first_column))
print("\tDiluent transfer volume: " + str(diluent_transfer_first_column))

# calculate amounts to transfer into remaining wells
serial_transfer_volume = int(df * desired_volume_serial_dilution)
diluent_transfer_volume = int(desired_volume_serial_dilution - serial_transfer_volume)
print("Into remaining " + str(num_columns - 1) + " columns:")
print("\tSerial trasfer volume: " + str(serial_transfer_volume))
print("\tDiluent transfer volume: " + str(diluent_transfer_volume))

# * TIPS (any volumes <= 20ul will be transfered with 50uL tips)
diluent_first_tips_loc = (
    "Position1" if diluent_transfer_first_column > 20 else "Position8"
)
serial_first_tips_loc = "Position1" if stock_transfer_first_column > 20 else "Position8"
diluent_tips_loc = "Position1" if diluent_transfer_volume > 20 else "Position8"
serial_tips_loc = "Position1" if serial_transfer_volume > 20 else "Position8"

# * MIXING VOLUME CALCULATIONS
# mix volume for first stock antibiotic transfer
if serial_first_tips_loc == "Position1":
    first_serial_mix_volume = (
        int(0.6 * desired_volume_serial_dilution)
        if desired_volume_serial_dilution < 200
        else int(0.6 * 200)
    )
elif serial_first_tips_loc == "Position8":
    first_serial_mix_volume = (
        int(0.6 * desired_volume_serial_dilution)
        if desired_volume_serial_dilution < 50
        else int(0.6 * 50)
    )
else:
    first_serial_mix_volume = 0

# mix volume for remaining serial transfers
if serial_tips_loc == "Position1":
    serial_mix_volume = (
        int(0.6 * desired_volume_serial_dilution)
        if desired_volume_serial_dilution < 200
        else int(0.6 * 200)
    )
elif serial_tips_loc == "Position8":
    serial_mix_volume = (
        int(0.6 * desired_volume_serial_dilution)
        if desired_volume_serial_dilution < 50
        else int(0.6 * 50)
    )
else:
    serial_mix_volume = 0

# * BLOWOFF VOLUME CALCLATIONS
# first diluent transfer
if diluent_first_tips_loc == "Position1":
    diluent_first_blowoff_volume = (
        blowoff_volume
        if (200 - diluent_transfer_first_column) >= blowoff_volume
        else (200 - diluent_transfer_first_column)
    )
elif diluent_first_tips_loc == "Position8":
    diluent_first_blowoff_volume = (
        blowoff_volume
        if (50 - diluent_transfer_first_column) >= blowoff_volume
        else (50 - diluent_transfer_first_column)
    )
else:
    diluent_first_blowoff_volume = 0

# remaining diluent transfers
if diluent_tips_loc == "Position1":
    diluent_blowoff_volume = (
        blowoff_volume
        if (200 - diluent_transfer_volume) >= blowoff_volume
        else (200 - diluent_transfer_volume)
    )
elif diluent_tips_loc == "Position8":
    diluent_blowoff_volume = (
        blowoff_volume
        if (50 - diluent_transfer_volume) >= blowoff_volume
        else (50 - diluent_transfer_volume)
    )
else:
    diluent_blowoff_volume = (
        0  # prevents the variable from being potentially unbound (should never happen)
    )

# first stock transfer
if serial_first_tips_loc == "Position1":
    serial_first_blowoff_volume = (
        blowoff_volume
        if (200 - stock_transfer_first_column) >= blowoff_volume
        else (200 - stock_transfer_first_column)
    )
elif serial_first_tips_loc == "Position8":
    serial_first_blowoff_volume = (
        blowoff_volume
        if (50 - stock_transfer_first_column) >= blowoff_volume
        else (50 - stock_transfer_first_column)
    )
else:
    serial_first_blowoff_volume = 0

# remaining serial transfers
if serial_tips_loc == "Position1":
    serial_blowoff_volume = (
        blowoff_volume
        if (200 - serial_transfer_volume) >= blowoff_volume
        else (200 - serial_transfer_volume)
    )
elif serial_tips_loc == "Position8":
    serial_blowoff_volume = (
        blowoff_volume
        if (50 - serial_transfer_volume) >= blowoff_volume
        else (50 - serial_transfer_volume)
    )
else:
    serial_blowoff_volume = 0


# * Begin generating step 2 protocol -> Dispense diluent
# Transfer the correct amount of diluent into the first column (0 uL if start cons not specified or = to stock cons)
if diluent_transfer_first_column > 0:
    soloSoft.getTip(
        diluent_first_tips_loc
    )  # get the correct diluent transfer tips for the first column
    soloSoft.aspirate(
        position="Position3",
        aspirate_volumes=ZAgilentReservoir_1row().setColumn(
            1, diluent_transfer_first_column
        ),
        aspirate_shift=[0, 0, 4],
        pre_aspirate=diluent_first_blowoff_volume,
    )
    soloSoft.dispense(
        position="Position6",
        dispense_volumes=GenericPlate96Well().setColumn(
            1, diluent_transfer_first_column
        ),
        dispense_shift=[0, 0, 2],
        blowoff=diluent_first_blowoff_volume,
    )

# dispense diluent into remaining columns
if (
    not diluent_first_tips_loc == diluent_tips_loc or diluent_transfer_first_column <= 0
):  # get new tips if you need to
    soloSoft.getTip(diluent_tips_loc)
for i in range(2, num_columns + 1):
    # TODO: implement volume management to prevent running out of lb media
    soloSoft.aspirate(
        position="Position3",
        aspirate_volumes=ZAgilentReservoir_1row().setColumn(1, diluent_transfer_volume),
        aspirate_shift=[0, 0, 4],
        pre_aspirate=diluent_blowoff_volume,
    )
    soloSoft.dispense(
        position="Position6",
        dispense_volumes=GenericPlate96Well().setColumn(i, diluent_transfer_volume),
        dispense_shift=[0, 0, 2],
        blowoff=diluent_blowoff_volume,
    )

# * Transfer the correct amount of antibiotic stock solution into first row of the dilution plate (may be empty/ may contain diluent)
if not serial_first_tips_loc == diluent_tips_loc:  # get new tips if you need to
    soloSoft.getTip(serial_first_tips_loc)
soloSoft.aspirate(
    position="Position3",
    aspirate_volumes=ZAgilentReservoir_1row().setColumn(2, stock_transfer_first_column),
    pre_aspirate=serial_first_blowoff_volume,
    mix_at_start=True,
    mix_cycles=serial_source_num_mixes_s2,
    mix_volume=stock_transfer_first_column,  # might be better to base this mixing volume off stock_volume <- not a viarble yet
    aspirate_shift=[0, 0, 4],
    dispense_height=4,
)
soloSoft.dispense(
    position="Position6",
    dispense_volumes=GenericPlate96Well().setColumn(1, stock_transfer_first_column),
    dispense_shift=[0, 0, 2],
    blowoff=serial_first_blowoff_volume,
    mix_at_finish=True,
    mix_cycles=num_mixes,
    mix_volume=serial_mix_volume,
    aspirate_height=2,
)

# Serial Dilute into the remaining wells
if not serial_tips_loc == serial_first_tips_loc:  # get new tips if you need to
    soloSoft.getTip(serial_tips_loc)
for i in range(1, num_columns - 1):
    soloSoft.aspirate(
        position="Position6",
        aspirate_volumes=GenericPlate96Well().setColumn(i, serial_transfer_volume),
        aspirate_shift=[0, 0, 2],
        pre_aspirate=serial_blowoff_volume,
        mix_at_start=True,
        mix_cycles=num_mixes,
        mix_volume=serial_mix_volume,
        dispense_height=2,
    )
    soloSoft.dispense(
        position="Position6",
        dispense_volumes=GenericPlate96Well().setColumn(i + 1, serial_transfer_volume),
        dispense_shift=[0, 0, 2],
        blowoff=serial_blowoff_volume,
        mix_at_finish=True,
        mix_cycles=num_mixes,
        mix_volume=serial_mix_volume,
        aspirate_height=2,
    )
# no need to throw away excess volume from last column of serial dilution

"""
STEP 3: ADD ANTIBIOTIC TO CULTURE PLATES -------------------------------------------------------------------------------------
"""
if (
    serial_transfer_volume <= 20
):  # get tips if you need to or are currently using 50 uL tips
    soloSoft.getTip()
for i in range(6, 0, -1):
    soloSoft.aspirate(
        position="Position6",
        aspirate_volumes=GenericPlate96Well().setColumn(
            i, antibiotic_transfer_volume_s3
        ),
        mix_at_start=True,
        mix_cycles=num_mixes,
        mix_volume=antibiotic_mix_volume_s3,
        dispense_height=2,
        aspirate_shift=[0, 0, 2],
        pre_aspirate=10,
    )
    soloSoft.dispense(
        position="Position4",
        dispense_volumes=GenericPlate96Well().setColumn(
            i, antibiotic_transfer_volume_s3
        ),
        mix_at_finish=True,
        mix_cycles=num_mixes,
        mix_volume=destination_mix_volume_s3,
        aspirate_height=2,
        dispense_shift=[0, 0, 2],
        blowoff=10,
    )

soloSoft.shuckTip()
soloSoft.savePipeline()

# Uncomment this section to run the program automatically through SoftLinx ------------------------------------------------

# initialize softLinx
softLinx = SoftLinx("Generate Protocol", "generate_protocol.slvp")
# add steps to the softLinx protocol
softLinx.soloSoftRun(
    "C:\\Users\\svcaibio\\Dev\\liquidhandling\\protocols\\campaign1\\generate_protocol.hso"
)
# save the protocol and generate .slvp and .ahk
softLinx.saveProtocol()
# # open the .ahk file to remotely start the program
# os.startfile("C:\\Users\\svcaibio\\Dev\\liquidhandling\\protocols\\campaign1\\generate_protocol.ahk")


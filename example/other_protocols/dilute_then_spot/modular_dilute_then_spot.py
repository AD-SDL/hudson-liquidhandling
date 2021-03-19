"""
Modular version of the protocol in dilute_then_spot.jpynb

TODO: Put this code into a well documented jupyter notebook if it works

Steps: 
- Dispense all media (same as before)
- Complete all serial dilutiions -> use the same tip for all dilutions (still switch tip between each half plate of course)
- Spot each well in dilution plate onto agar plate (mix a few times before each spot -> pre-wetting) -> also get a new tip each time

"""

from liquidhandling import SoloSoft, SoftLinx
from liquidhandling import *  # replace with plate types used

# * Program Variables ------------------
stock_start_column = 5
spot_z_shift = 2.2

media_aspirate_column = 1
first_column_transfer_volume = 100
dilution_media_volume = 90
dilution_transfer_volume = 10
stock_mix_volume = 50
dilution_mix_volume = 30  # 50uL tips used
num_mixes = 5

pre_spot_mix_volume = 30

default_z_shift = 2
pre_spot_aspirate_volume = 10
spot_volume = 3.5
# * ---------------------------------------
soloSoft = SoloSoft(
    filename="modular_dilute_then_spot_STEP1.hso",
    plateList=[
        "TipBox.200uL.Corning-4864.orangebox",
        "Empty",
        "Reservoir.12col.Agilent-201256-100.BATSgroup",
        "Empty",
        "Plate.96.Corning-3635.ClearUVAssay",
        "Plate.96.Corning-3635.ClearUVAssay",
        "TipBox.50uL.Axygen-EV-50-R-S.tealbox",
        "AgarPlate.40mL.OmniTray-242811.ColonyPicker",
    ],
)

# * STEP 1: Dispense diluent into whole plate -> MUST CHECK/REFILL BETWEEN CREATING EACH PLATE -------------
soloSoft.getTip()
# Don't dispense diluent into first column of each half plate -> will be pure stock
for i in range(2, 7):  # first half of the plate, columns 2-6
    soloSoft.aspirate(
        position="Position3",
        aspirate_volumes=Reservoir_12col_Agilent_201256_100_BATSgroup().setColumn(
            media_aspirate_column, dilution_media_volume
        ),
        aspirate_shift=[0, 0, 4],
    )
    soloSoft.dispense(
        position="Position6",
        dispense_volumes=Plate_96_Corning_3635_ClearUVAssay().setColumn(
            i, dilution_media_volume
        ),
        dispense_shift=[0, 0, default_z_shift],
    )
media_aspirate_column += 1
for i in range(8, 13):  # second half of the plate, columns 8-12
    soloSoft.aspirate(
        position="Position3",
        aspirate_volumes=Reservoir_12col_Agilent_201256_100_BATSgroup().setColumn(
            media_aspirate_column, dilution_media_volume
        ),
        aspirate_shift=[0, 0, 4],
    )
    soloSoft.dispense(
        position="Position6",
        dispense_volumes=Plate_96_Corning_3635_ClearUVAssay().setColumn(
            i, dilution_media_volume
        ),
        dispense_shift=[0, 0, default_z_shift],
    )
soloSoft.shuckTip()
soloSoft.savePipeline()

# * STEP2 SERIAL DILUTION FOR BOTH HALVES OF THE PLATE ----------------------------------------------------------------

soloSoft = SoloSoft(
    filename="modular_dilute_then_spot_STEP2.hso",
    plateList=[
        "TipBox.200uL.Corning-4864.orangebox",
        "Empty",
        "Reservoir.12col.Agilent-201256-100.BATSgroup",
        "Empty",
        "Plate.96.Corning-3635.ClearUVAssay",
        "Plate.96.Corning-3635.ClearUVAssay",
        "TipBox.50uL.Axygen-EV-50-R-S.tealbox",
        "AgarPlate.40mL.OmniTray-242811.ColonyPicker",
    ],
)
# FIRST HALF OF THE PLATE
for i in range(1, 3):
    # set up first column of dilution plate -> pure stock, no dilution (100uL transfer volume)
    soloSoft.getTip()  # 200uL tips
    soloSoft.aspirate(
        position="Position5",
        aspirate_volumes=Plate_96_Corning_3635_ClearUVAssay().setColumn(
            stock_start_column, first_column_transfer_volume
        ),
        aspirate_shift=[0, 0, default_z_shift],
        mix_at_start=True,
        mix_volume=stock_mix_volume,
        mix_cycles=num_mixes,
        dispense_height=default_z_shift,
    )
    soloSoft.dispense(
        position="Position6",
        dispense_volumes=Plate_96_Corning_3635_ClearUVAssay().setColumn(
            (6 * (i - 1)) + 1, first_column_transfer_volume
        ),
        dispense_shift=[0, 0, default_z_shift],
        mix_at_finish=True,
        mix_volume=dilution_mix_volume,
        mix_cycles=num_mixes,
        aspirate_height=default_z_shift,
    )
    print("Prepare the first dilution column: ")
    print(
        "\t From clear UV column ( "
        + str(stock_start_column)
        + " ) to clear dilution UV column ( "
        + str((6 * (i - 1)) + 1)
        + " )"
    )

    print("Diluting: ")
    soloSoft.getTip("Position7")  # 50uL tips for 10uL transfers
    for j in range(1, 6):  # 1,2,3,4,5
        soloSoft.aspirate(
            position="Position6",
            aspirate_volumes=Plate_96_Corning_3635_ClearUVAssay().setColumn(
                (6 * (i - 1)) + j, dilution_transfer_volume
            ),
            aspirate_shift=[0, 0, default_z_shift],
            mix_at_start=True,
            mix_cycles=num_mixes,
            mix_volume=dilution_mix_volume,
            dispense_height=default_z_shift,
        )
        soloSoft.dispense(
            position="Position6",
            dispense_volumes=Plate_96_Corning_3635_ClearUVAssay().setColumn(
                (6 * (i - 1)) + j + 1, dilution_transfer_volume
            ),
            dispense_shift=[0, 0, default_z_shift],
            mix_at_finish=True,
            mix_cycles=num_mixes,
            mix_volume=dilution_mix_volume,
            aspirate_height=default_z_shift,
        )

        print(
            "\t Dilute:  From clear UV column ( "
            + str((6 * (i - 1)) + j)
            + " ) to clear UV column ( "
            + str((6 * (i - 1)) + j + 1)
            + " )"
        )

    stock_start_column += 1  # make sure to draw from the next culture stock column for the next half of the plate.

soloSoft.shuckTip()
soloSoft.savePipeline()

# * STEP 3 SPOT ALL DILUTIONS -----------------------------------------------------------------------------

soloSoft = SoloSoft(
    filename="modular_dilute_then_spot_STEP3.hso",
    plateList=[
        "TipBox.200uL.Corning-4864.orangebox",
        "Empty",
        "Reservoir.12col.Agilent-201256-100.BATSgroup",
        "Empty",
        "Plate.96.Corning-3635.ClearUVAssay",
        "Plate.96.Corning-3635.ClearUVAssay",
        "TipBox.50uL.Axygen-EV-50-R-S.tealbox",
        "AgarPlate.40mL.OmniTray-242811.ColonyPicker",
    ],
)

print("Spotting: ")
for i in range(1, 13):
    soloSoft.getTip("Position7")

    soloSoft.aspirate(  # mix before aspirating the 3.5 uL
        position="Position6",
        aspirate_volumes=Plate_96_Corning_3635_ClearUVAssay().setColumn(
            i, pre_spot_aspirate_volume
        ),
        aspirate_shift=[0, 0, default_z_shift],
        mix_at_start=True,
        mix_volume=pre_spot_mix_volume,
        dispense_height=default_z_shift,
        mix_cycles=num_mixes,
    )
    soloSoft.dispense(
        position="Position8",
        dispense_volumes=AgarPlate_40mL_OmniTray_242811_ColonyPicker().setColumn(
            i, spot_volume
        ),
        dispense_shift=[0, 0, spot_z_shift],
    )
    print(
        "Dilution Plate Column ( "
        + str(i)
        + " ) -> Agar Plate Column ( "
        + str(i)
        + " )"
    )

soloSoft.shuckTip()
soloSoft.savePipeline()

# LOAD PROTOCOL STEPS 1-3 IN SOFTLINX
softLinx = SoftLinx(
    "Modular Dilute then Spot Steps 1-3", "modular_dilute_then_spot.slvp"
)
softLinx.soloSoftRun(
    "C:\\Users\\svcaibio\\Dev\\liquidhandling\\example\\other_protocols\\dilute_then_spot\\modular_dilute_then_spot_STEP1.hso"
)
softLinx.soloSoftRun(
    "C:\\Users\\svcaibio\\Dev\\liquidhandling\\example\\other_protocols\\dilute_then_spot\\modular_dilute_then_spot_STEP2.hso"
)
softLinx.soloSoftRun(
    "C:\\Users\\svcaibio\\Dev\\liquidhandling\\example\\other_protocols\\dilute_then_spot\\modular_dilute_then_spot_STEP3.hso"
)
softLinx.saveProtocol()

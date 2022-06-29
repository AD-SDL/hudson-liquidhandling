import argparse
import os
import sys
import time
from subprocess import Popen
from liquidhandling import *
from tip_utils import replace_tip_box, remove_tip_box

# * Transfers media from resevoir in position 1 to given columns in 384 well assay plate in position 4
def generate_media_transfer_to_half_assay_hso(directory_path,
filename,
media_start_column,
media_z_shift, 
media_transfer_volume_s1,
flat_bottom_z_shift,
start_col, # provide column to start dispense on assay plate
end_col, # provide column to end dispense on assay plate
k): # k = current treatment number


    # * Initialize soloSoft (step 1)
    step1_hso_filename = os.path.join(directory_path, f"plate{k}_"+ filename)
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

    # hudson01_hso_path = # * TODO: FIGURE OUT PATH NAME

    return filename


# * Transfers media from resevoir in position 1 to given columns in 384 well assay plate in position 4
def generate_media_transfer_to_half_assay_loop_hso(directory_path,
filename,
media_start_column,
media_z_shift, 
media_transfer_volume_s1,
flat_bottom_z_shift,
start_col, # provide column to start dispense on assay plate
end_col, # provide column to end dispense on assay plate
k): # k = current treatment number


    # * Initialize soloSoft (step 1)
    step1_hso_filename = os.path.join(directory_path, f"plate{k}_"+ filename)
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

    soloSoft.aspirate(
            position="Position1",
            aspirate_volumes=Reservoir_12col_Agilent_201256_100_BATSgroup().setColumn(
                media_start_column[k], 120
            ),
            aspirate_shift=[0, 0, media_z_shift],
        )

    for i in range(start_col, end_col+1):  # first quarter plate = media from column 1
        
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
                media_start_column[k], 120
            ),
            aspirate_shift=[0, 0, media_z_shift],
        )
    
    for i in range(start_col, end_col+1):

        dispense_volumes_startB = Plate_384_Corning_3540_BlackwClearBottomAssay().setColumn(
                i, media_transfer_volume_s1
            )
        dispense_volumes_startB[0][i-1] = 0
        soloSoft.dispense(
            position="Position4",
            dispense_volumes= dispense_volumes_startB,
            dispense_shift=[0, 0, flat_bottom_z_shift],
        )
    
    soloSoft.aspirate(
            position="Position1",
            aspirate_volumes=Reservoir_12col_Agilent_201256_100_BATSgroup().setColumn(
                media_start_column[k] + 1, 120
            ),
            aspirate_shift=[0, 0, media_z_shift],
        )
        
    for i in range(start_col+6, end_col+7):  # second quarter plate = media from column 2
        
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
            media_start_column[k] + 1, 120
        ),
        aspirate_shift=[0, 0, media_z_shift],
    )

    for i in range(start_col+6, end_col+7):
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

    # hudson01_hso_path = # * TODO: FIGURE OUT PATH NAME

    return filename


# * Fill culture dilution resevoir and treatment plates with media
def generate_fill_culture_dilution_and_treatment_plates_with_media_hso(directory_path,
filename,
media_start_column,
media_z_shift,
flat_bottom_z_shift,
reservoir_z_shift,
half_dilution_media_volume,
dilution_culture_volume,
culture_plate_num_mix,
culture_plate_mix_volume_s1,
culture_dil_column,
k,
culture_column,
num_mixes,
culture_dilution_num_mix,
culture_dilution_mix_volume
):
    step1_cell_dilution_hso_filename = os.path.join(directory_path, f"plate{k}_" + filename)
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
filename,
media_start_column,
media_z_shift,
flat_bottom_z_shift,
reservoir_z_shift,
culture_transfer_volume_s1,
culture_dil_column,
num_mixes,
growth_plate_mix_volume_s1,
start_col,
end_col,
k
):
    step1_cells_to_assay_first_half_hso_filename = os.path.join(directory_path, f"plate{k}_" + filename)
    # step1_hso_filename_list.append(step1_cells_to_assay_first_half_hso_filename)
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
            pre_aspirate=10,
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
            blowoff=10,
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
            pre_aspirate=10,
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
            blowoff=10,
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
            pre_aspirate=10,
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
            blowoff=10,
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
            pre_aspirate=10,
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
            blowoff=10,
        )
    
    soloSoft.shuckTip()
    soloSoft.savePipeline()

    return filename


# * Adds diluted cells to assay plate
def generate_add_diluted_cells_to_assay_loop_hso(directory_path,
filename,
media_start_column,
media_z_shift,
flat_bottom_z_shift,
reservoir_z_shift,
culture_transfer_volume_s1,
culture_dil_column,
num_mixes,
growth_plate_mix_volume_s1,
start_col,
end_col,
k
):
    step1_cells_to_assay_first_half_hso_filename = os.path.join(directory_path, f"plate{k}_" + filename)
    # step1_hso_filename_list.append(step1_cells_to_assay_first_half_hso_filename)
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
    soloSoft.aspirate(  # well in first half
            position="Position7",
            aspirate_volumes=Reservoir_12col_Agilent_201256_100_BATSgroup().setColumn(
                culture_dil_column[k], 120
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
    for i in range(start_col, end_col+1):  # trying a different method of cell dispensing (09/07/21)
        
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
            culture_dil_column[k], 120
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
    for i in range(start_col, end_col+1):

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
            culture_dil_column[k], 120
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
    for i in range(start_col+12, end_col+13):
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
    soloSoft.aspirate(  # well in second half
        position="Position7",
        aspirate_volumes=Reservoir_12col_Agilent_201256_100_BATSgroup().setColumn(
            culture_dil_column[k], 120
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
    for i in range(start_col+12, end_col+13):

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
    
    soloSoft.shuckTip()
    soloSoft.savePipeline()

    return filename


#* Step 2, performs serial dilution on treatment plate
def generate_serial_dlution_treatment_hso(directory_path,
filename,
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
k,
num_mixes
):

        # * Initialize soloSoft (step 2)
    step2_hso_filename = os.path.join(directory_path, f"plate{k}_" + filename)
    # step2_hso_filename_list.append(step2_hso_filename)
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

    # * here
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

# * adds antibiotic to assay plate (first half)
def generate_add_antibioitc_to_assay_first_half_hso(directory_path,
filename,
treatment_dil_half,
antibiotic_transfer_volume_s3,
num_mixes,
antibiotic_mix_volume_s3,
resevoir_z_shift,
destination_mix_volume_s3,
flat_bottom_z_shift,
start_col,
end_col,
k,
reservoir_z_shift
):
    step3_hso_filename = os.path.join(directory_path, f"plate{k}_"+ filename)
    # step3_hso_filename_list.append(step3_hso_filename)
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
                i + start_col, antibiotic_transfer_volume_s3
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
                i + start_col, antibiotic_transfer_volume_s3
            )
        dispense_volumes_startB[0][i+start_col-1] = 0

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
                i + end_col, antibiotic_transfer_volume_s3
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
                i + end_col, antibiotic_transfer_volume_s3
            )
        dispense_volumes_startB[0][i+end_col-1] = 0

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


def generate_add_antibioitc_to_assay_second_half_hso(directory_path,
filename,
treatment_dil_half,
antibiotic_transfer_volume_s3,
num_mixes,
antibiotic_mix_volume_s3,
resevoir_z_shift,
destination_mix_volume_s3,
flat_bottom_z_shift,
start_col,
end_col,
k,
reservoir_z_shift
):
    step3_hso_filename = os.path.join(directory_path, f"plate{k}_"+ filename)
    # step3_hso_filename_list.append(step3_hso_filename)
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
                (6 * (treatment_dil_half[k] - 1)) + i - 6, antibiotic_transfer_volume_s3 # difference here
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
                i + start_col, antibiotic_transfer_volume_s3
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
                (6 * (treatment_dil_half[k] - 1)) + i - 6, antibiotic_transfer_volume_s3
            ),
            mix_at_start=True,
            mix_cycles=num_mixes,
            mix_volume=antibiotic_mix_volume_s3,
            dispense_height=reservoir_z_shift,
            aspirate_shift=[0, 0, reservoir_z_shift],
        )

        dispense_volumes_startB = Plate_384_Corning_3540_BlackwClearBottomAssay().setColumn(
                i + start_col, antibiotic_transfer_volume_s3
            )
        dispense_volumes_startB[0][i+start_col-1] = 0

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
                (6 * (treatment_dil_half[k] - 1)) + i - 6, antibiotic_transfer_volume_s3
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
                i + end_col, antibiotic_transfer_volume_s3
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
                (6 * (treatment_dil_half[k] - 1)) + i - 6, antibiotic_transfer_volume_s3
            ),
            mix_at_start=True,
            mix_cycles=num_mixes,
            mix_volume=antibiotic_mix_volume_s3,
            dispense_height=reservoir_z_shift,
            aspirate_shift=[0, 0, reservoir_z_shift],
        )
        dispense_volumes_startB = Plate_384_Corning_3540_BlackwClearBottomAssay().setColumn(
                i + end_col, antibiotic_transfer_volume_s3
            )
        dispense_volumes_startB[0][i+end_col-1] = 0

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
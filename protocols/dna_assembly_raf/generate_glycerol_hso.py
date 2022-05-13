import os
from liquidhandling import SoloSoft
from liquidhandling import Reservoir_12col_Agilent_201256_100_BATSgroup
from liquidhandling import Plate_96_Corning_3635_ClearUVAssay


def generate_glycerol_hso(file_path, directory_name, volume, num_mix, origin_mix_volume, destination_mix_volume, origin_z_shift, destination_z_shift):
    """generate_glycerol_hso

    Description: TODO

    Parameters: TODO

    Returns: TODO

    # TODO: maybe use larger tips to make this faster

    """
    soloSoft = SoloSoft(
        filename=file_path,
        plateList=[
            "DeepBlock.96.VWR-75870-792.sterile",
            "Empty",
            "TipBox.180uL.Axygen-EVF-180-R-S.bluebox", 
            "Plate.96.Corning-3635.ClearUVAssay",
            "Empty",
            "Plate.96.Corning-3635.ClearUVAssay",
            "Empty",
            "Empty",
        ],
    )

    for i in range(1,13):  # for each column in the whole plate
        soloSoft.getTip("Position3")
        soloSoft.aspirate(
            position="Position1", # glycerol stock 96 deep well
            aspirate_volumes=Reservoir_12col_Agilent_201256_100_BATSgroup().setColumn(1, volume),
            aspirate_shift=[0,0,origin_z_shift], 
            mix_at_start=True, 
            mix_cycles=num_mix, 
            mix_volume=origin_mix_volume,
            dispense_height=origin_z_shift,
            syringe_speed=75,
        )
        soloSoft.dispense(
            position="Position6", # master plate
            dispense_volumes=Plate_96_Corning_3635_ClearUVAssay().setColumn(i, volume),
            dispense_shift=[0,0,destination_z_shift],
            mix_at_finish=True, 
            mix_cycles=num_mix, 
            mix_volume=destination_mix_volume, 
            aspirate_height=destination_z_shift,
            syringe_speed=75,
        )

    soloSoft.shuckTip()
    soloSoft.savePipeline()

    hudson01_hso_path = "C:\\labautomation\\instructions\\" + directory_name + "\\" + os.path.basename(file_path)
    print(hudson01_hso_path)

    return hudson01_hso_path 


import os
from liquidhandling import SoloSoft
from liquidhandling import Plate_96_Corning_3635_ClearUVAssay


def generate_hso(
    file_path, 
    directory_name, 
    volume, 
    num_mix, 
    origin_mix_volume, 
    destination_mix_volume, 
    origin_z_shift, 
    destination_z_shift):
    """ generate_delection_hso

        Description: Generates the SOLO .hso files for creating the selection plates

        Parameters:
            filename: filepath to sa
            origin_wells: list of wells in origin plate to aspirate from (ex. ["A1", "A2", "A3", ...])
            destination_wells: list of wells in destination plate to dispense into (ex. ["B1", "B2", "B3", ...])
                note: in the above examples, A1 -> B1, A2 -> B2, A3 -> B3. Both lists must be same length
            volume: volume of liquid to transfer from origin to destination
            num_mix: 
            origin_mix_volume: mix volume before aspiration
            destination_mix_volume: mix volume after dispense 
            origin_z_shift: distance from well bottom (mm) to aspirate
            destination_z_shift: distance from well bottom (mm) to dispense
    
    """
    two_transfers = False 
    if volume > 50: 
        volume = float(volume)/float(2)
        two_transfers = True

    soloSoft = SoloSoft(
        filename=file_path,
        plateList=[
            "DeepBlock.96.VWR-75870-792.sterile", # Position1
            "Empty",  # Position2
            "TipBox.50uL.Axygen-EV-50-R-S.tealbox",  # Position3
            "Plate.96.Corning-3635.ClearUVAssay",   # Position4
            "Empty", # Position5
            "Plate.96.Corning-3635.ClearUVAssay",  # Position6
            "Empty",  # Position7
            "Empty",  # Position8
        ],
    )
    
    for i in range(1,13):  # for every column in the plate
        soloSoft.getTip("Position3")
        soloSoft.aspirate(
            position="Position6", 
            aspirate_volumes=Plate_96_Corning_3635_ClearUVAssay().setColumn(i, volume),
            aspirate_shift=[0,0,origin_z_shift], 
            mix_at_start=True, 
            mix_cycles=num_mix, 
            mix_volume=origin_mix_volume,
            dispense_height=origin_z_shift,
        )
        soloSoft.dispense(
            position="Position4", 
            dispense_volumes=Plate_96_Corning_3635_ClearUVAssay().setColumn(i, volume),
            dispense_shift=[0,0,destination_z_shift],
            mix_at_finish=True, 
            mix_cycles=num_mix, 
            mix_volume=destination_mix_volume, 
            aspirate_height=destination_z_shift,
        )

        if two_transfers == True: # TODO: Remove this, not necessary anymore
            soloSoft.aspirate(
                position="Position6", 
                aspirate_volumes=Plate_96_Corning_3635_ClearUVAssay().setColumn(i, volume),
                aspirate_shift=[0,0,origin_z_shift], 
                mix_at_start=True, 
                mix_cycles=num_mix, 
                mix_volume=origin_mix_volume,
                dispense_height=origin_z_shift,
            )
            soloSoft.dispense(
                position="Position4", 
                dispense_volumes=Plate_96_Corning_3635_ClearUVAssay().setColumn(i, volume),
                dispense_shift=[0,0,destination_z_shift],
                mix_at_finish=True, 
                mix_cycles=num_mix, 
                mix_volume=destination_mix_volume, 
                aspirate_height=destination_z_shift,
            )

    soloSoft.shuckTip()
    soloSoft.savePipeline()

    hudson01_hso_path = "C:\\labautomation\\instructions\\" + directory_name + "\\" + os.path.basename(file_path)
    print(hudson01_hso_path)

    return hudson01_hso_path 

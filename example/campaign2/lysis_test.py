from liquidhandling import SoloSoft, SoftLinx
from liquidhandling import Reservoir_12col_Agilent_201256_100_BATSgroup

#* Program Variables
aspirate_volume = 22.2
aspirate_mix_volume = 20
aspirate_num_mixes = 3
aspirate_syringe_speed = 25 
default_z_shift = .5  # TODO: TEST THIS!
default_blowoff = 0
aspirate_column = 12
dispense_column = 11

#* Initialize solosoft and deck layout 
soloSoft = SoloSoft(
    filename="lysis_test.hso", 
    plateList=[
        "TipBox.200uL.Corning-4864.orangebox", 
        "Empty", 
        "Reservoir.12col.Agilent-201256-100.BATSgroup", 
        "Plate.96.Corning-3635.ClearUVAssay", 
        "Plate.96.PlateOne-1833-9600.ConicalBottomStorage", 
        "Plate.96.PlateOne-1833-9600.ConicalBottomStorage", 
        "TipBox.50uL.Axygen-EV-50-R-S.tealbox", 
        "Empty"
    ]
)

soloSoft.getTip()

for i in range(12):
    soloSoft.aspirate(
        position="Position3", 
        aspirate_volumes = Reservoir_12col_Agilent_201256_100_BATSgroup().setColumn(aspirate_column, aspirate_volume),
        aspirate_shift=[0,0,default_z_shift],
        pre_aspirate=default_blowoff,
        # mix_at_start=True, 
        # mix_cycles=aspirate_num_mixes, 
        # mix_volume=aspirate_mix_volume, 
        # dispense_height=default_z_shift,
        syringe_speed=aspirate_syringe_speed,

    )
    soloSoft.dispense(
        position="Position3", 
        dispense_volumes=Reservoir_12col_Agilent_201256_100_BATSgroup().setColumn(dispense_column, aspirate_volume), 
        dispense_shift=[0,0,default_z_shift],
        blowoff=default_blowoff,
        syringe_speed=aspirate_syringe_speed,
    )

soloSoft.shuckTip()
soloSoft.savePipeline()

softLinx = SoftLinx("Lysis Test", "lysis_test.slvp")
softLinx.soloSoftRun("C:\\labautomation\\instructions\\lysis_test.hso")
softLinx.saveProtocol()

from liquidhandling import SoloSoft, SoftLinx
from liquidhandling import Plate_96_Corning_3635_ClearUVAssay


# ----------------------------------------------------------------------------------------
soloSoft = SoloSoft(
    filename="C:\\Users\\svcaibio\\Desktop\\Debug\\test_20.hso",
    plateList=[
        "TipBox.50uL.Axygen-EV-50-R-S.tealbox",
        "Empty",
        "Empty",
        "Empty",
        "Empty",
        "Plate.96.Corning-3635.ClearUVAssay",
        "Empty",
        "Plate.96.Corning-3635.ClearUVAssay",
    ],
)

soloSoft.getTip()

soloSoft.aspirate(
    position="Position8", 
    aspirate_volumes=Plate_96_Corning_3635_ClearUVAssay().setColumn(2, 20),
    aspirate_shift=[0, 0, 2],
    mix_at_start=True,
    mix_cycles=3,
    mix_volume=30,
    dispense_height=2,
    pre_aspirate=10,
)

soloSoft.dispense(
    position="Position6", 
    dispense_volumes=Plate_96_Corning_3635_ClearUVAssay().setColumn(5,20),
    dispense_shift=[0,0,2],
    mix_at_finish=True,
    mix_cycles=3,
    mix_volume=20,
    aspirate_height=2,
    blowoff=10,
)

soloSoft.shuckTip()
soloSoft.savePipeline()
# ----------------------------------------------------------------------------------

softLinx = SoftLinx("Test 20", "C:\\Users\\svcaibio\\Desktop\\Debug\\test_20.slvp")

softLinx.setPlates(
    {"SoftLinx.Solo.Position6": "Plate.96.Corning-3635.ClearUVAssay"}
)

softLinx.soloSoftRun("C:\\Users\\svcaibio\\Desktop\\Debug\\test_20.hso")

softLinx.plateCraneMovePlate(["SoftLinx.Solo.Position6"],["SoftLinx.PlateCrane.Stack5"])

softLinx.plateCraneMoveCrane("SoftLinx.PlateCrane.Safe")

softLinx.saveProtocol()



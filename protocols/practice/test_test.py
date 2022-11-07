from liquidhandling import SoloSoft
from liquidhandling import *


# ----------------------------------------------------------------------------------------
soloSoft = SoloSoft(
    filename="C:\\Users\\svcaibio\\Desktop\\Debug\\zahmeeth_test_code.hso",
    plateList=[
        "Empty",
        "Empty",
        "TipBox.50uL.Axygen-EV-50-R-S.tealbox",
        "Plate.96.Corning-3635.ClearUVAssay",
        "Empty",
        "Empty",
        "Empty",
        "Empty",
    ],
)

soloSoft.getTip("Position3")

soloSoft.aspirate(
    position="Position4", 
    aspirate_volumes=Plate_96_Corning_3635_ClearUVAssay().setColumn(1, 30),
    aspirate_shift=[0, 0, 2],
    # mix_at_start=True,
    # mix_cycles=3,
    # mix_volume=30,
    # dispense_height=2,
    # # pre_aspirate=10,
)

soloSoft.dispense(
    position="Position4", 
    dispense_volumes=Plate_96_Corning_3635_ClearUVAssay().setColumn(12,30),
    dispense_shift=[0,0,2],
    # mix_at_finish=True,
    # mix_cycles=3,
    # mix_volume=20,
    # aspirate_height=2,
    # blowoff=10,
)

soloSoft.shuckTip()
soloSoft.savePipeline()
# ---------------------------------------------------------------------------------


softLinx = SoftLinx("Zahmeeth SoftLinx Code", "C:\\Users\\svcaibio\\Desktop\\Debug\\zahmeeth_softLinx_code.slvp")

softLinx.setPlates(
    {"SoftLinx.PlateCrane.Stack5": "Plate.96.Corning-3635.ClearUVAssay"}
)

softLinx.plateCraneMovePlate(["SoftLinx.PlateCrane.Stack5"],["SoftLinx.Solo.Position4"])

softLinx.plateCraneRemoveLid(["SoftLinx.Solo.Position4"],["SoftLinx.PlateCrane.LidNest2"])

softLinx.plateCraneMoveCrane("SoftLinx.PlateCrane.Safe")

softLinx.soloSoftRun("C:\\Users\\svcaibio\\Desktop\\Debug\\zahmeeth_test_code.hso")

softLinx.plateCraneMovePlate(["SoftLinx.Solo.Position4"], ["SoftLinx.Hidex.Nest"])

softLinx.hidexRun("pyhamilton")

softLinx.plateCraneMovePlate(["SoftLinx.Hidex.Nest"], ["SoftLinx.Liconic.Nest"])

softLinx.plateCraneReplaceLid(["SoftLinx.PlateCrane.LidNest2"],["SoftLinx.Liconic.Nest"])

softLinx.liconicLoadIncubator()


# softLinx.soloSoftRun("C:\\Users\\svcaibio\\Desktop\\Debug\\test_20.hso")

# softLinx.plateCraneMovePlate([],["SoftLinx.PlateCrane.Stack5"])

# softLinx.plateCraneMoveCrane("SoftLinx.PlateCrane.Safe")

# softLinx.saveProtocol()

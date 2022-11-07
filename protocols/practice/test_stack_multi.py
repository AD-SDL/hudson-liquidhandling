from liquidhandling import SoftLinx

softLinx = SoftLinx("TestStackMulti", "C:\\Users\\svcaibio\\Desktop\\Debug\\TestStackMulti.slvp")

# start with 2 ClearUVAssay plates and one TipBox in stacks 
softLinx.setPlates(
    {"SoftLinx.PlateCrane.Stack5": "Plate.96.Corning-3635.ClearUVAssay", 
    "SoftLinx.PlateCrane.Stack4": "TipBox.180uL.Axygen-EVF-180-R-S.bluebox"}
)

# Move assay plate
softLinx.plateCraneMovePlate(["SoftLinx.PlateCrane.Stack5"], ["SoftLinx.Solo.Position4"], poolID=1)

# TEST Remove Lid with pool ID
softLinx.plateCraneRemoveLid(["SoftLinx.Solo.Position4"], ["SoftLinx.PlateCrane.LidNest2"])

# TEST Replace Lid with pool ID
softLinx.plateCraneReplaceLid(["SoftLinx.PlateCrane.LidNest2"],["SoftLinx.Solo.Position4"])

# # Move Tip Box 
# softLinx.plateCraneMovePlate(["SoftLinx.PlateCrane.Stack4"], ["SoftLinx.PlateCrane.Stack3"], hasLid=True,poolID=2)

# # Move Assay plate
# softLinx.plateCraneMovePlate(["SoftLinx.PlateCrane.Stack5"], ["SoftLinx.PlateCrane.Stack1"],poolID=1)

# # TEST Remove Lid with pool ID
# softLinx.plateCraneRemoveLid(["SoftLinx.PlateCrane.Stack5"], ["SoftLinx.PlateCrane.LidNest1"])

# # TEST Replace Lid with pool ID
# softLinx.plateCraneReplaceLid(["SoftLinx.PlateCrane.Stack5"],["SoftLinx.PlateCrane.Stack1"], poolID=5)

# save softLinx protocol 
softLinx.saveProtocol()
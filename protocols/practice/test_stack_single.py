from liquidhandling import SoftLinx

softLinx = SoftLinx("TestStackSingle", "C:\\Users\\svcaibio\\Desktop\\Debug\\TestStackSingle.slvp")

# start with 2 ClearUVAssay plates and one TipBox in stacks 
softLinx.setPlates(
    {"SoftLinx.PlateCrane.Stack5": "Plate.96.Corning-3635.ClearUVAssay"}
)

# Move assay plate
softLinx.plateCraneMovePlate(["SoftLinx.PlateCrane.Stack5"], ["SoftLinx.PlateCrane.Stack1"])

# Move Assay plate
softLinx.plateCraneMovePlate(["SoftLinx.PlateCrane.Stack5"], ["SoftLinx.PlateCrane.Stack1"])

# save softLinx protocol 
softLinx.saveProtocol()
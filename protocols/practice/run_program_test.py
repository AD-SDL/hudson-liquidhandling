from liquidhandling import SoftLinx

# Initialize SoftLinx
softLinx = SoftLinx("Run Program Test", "run_program_test.slvp")

# Move plate from stack onto Solo deck pos 4 
softLinx.setPlates({"SoftLinx.PlateCrane.Stack5": "Plate.96.Corning-3635.ClearUVAssay"})
softLinx.plateCraneMovePlate(["SoftLinx.PlateCrane.Stack5"], ["SoftLinx.Solo.Position4"])
softLinx.plateCraneMoveCrane("SoftLinx.PlateCrane.Safe")

# Move plate from Solo deck pos 4 to Hidex Nest
softLinx.plateCraneMovePlate(
        ["SoftLinx.Solo.Position4"], ["SoftLinx.Hidex.Nest"]
    )  # no need to open hidex
softLinx.hidexClose()
softLinx.plateCraneMoveCrane("SoftLinx.PlateCrane.Safe")

# Run Hidex Protocol 
softLinx.hidexRun("Campaign1") 

# Transfer Hidex data from C:\labautomation\data to compute cell (lambda6)
softLinx.runProgram("C:\\Users\\svcaibio\\Dev\\liquidhandling\\zeromq\\utils\\send_data.bat")

softLinx.saveProtocol()


import sys
import os

# Change this path to point to the location of the repository, if neccessary
sys.path.append(
    os.path.abspath(
        os.path.join(os.path.abspath(os.path.dirname(__file__)), "../../src")
    )
)
import SoftLinx
import SoloSoft

soloSoft = SoloSoft.SoloSoft("example.hso")

soloSoft.moveArm("Position1")
soloSoft.savePipeline()


softLinx = SoftLinx.SoftLinx("ExampleProtocol", "example_protocol.slvp")
softLinx.setPlates({"SoftLinx.PlateCrane.Stack1": "PlateOne 96 V-Bottom"})
softLinx.plateCraneMovePlate(["SoftLinx.PlateCrane.Stack1"], ["SoftLinx.Solo.Position6"])
softLinx.plateCraneMoveCrane("SoftLinx.PlateCrane.Safe")
softLinx.soloSoftRun(
"C:\\Users\\svcaibio\\Dev\\liquidhandling\\example\\softlinx\\example.hso"
)
softLinx.saveProtocol()

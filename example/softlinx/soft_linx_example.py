import sys
import os

# Change this path to point to the location of the repository, if neccessary
sys.path.append(
    os.path.abspath(
        os.path.join(os.path.abspath(os.path.dirname(__file__)), "../../src")
    )
)
import SoftLinx

softLinx = SoftLinx.SoftLinx("ExampleProtocol", "example_protocol.slvp")
softLinx.setPlates({"SoftLinx.PlateCrane.Stack1": "Falcon 96"})
# softLinx.plateCraneMovePlate()
softLinx.soloSoftRun(
    "C:\\Users\\ryand\\Dev\\repos\\liquidhandling\\example\\solosoft\\example.hso"
)
softLinx.saveProtocol()

# SoftLinx

TODO

## Examples and Usage

Basic example:

```python
from liquidhandling import SoftLinx
from liquidhandling import SoloSoft

soloSoft = SoloSoft("example.hso")

soloSoft.moveArm("Position1")
soloSoft.savePipeline()


softLinx = SoftLinx("ExampleProtocol", "example_protocol.slvp")
softLinx.setPlates({"SoftLinx.PlateCrane.Stack1": "PlateOne 96 V-Bottom"})
softLinx.plateCraneMovePlate(
    ["SoftLinx.PlateCrane.Stack1"], ["SoftLinx.Solo.Position6"]
)
softLinx.plateCraneMoveCrane("SoftLinx.PlateCrane.Safe")
softLinx.soloSoftRun(
    "C:\\Users\\svcaibio\\Dev\\liquidhandling\\example\\softlinx\\example.hso"
)
softLinx.soloSoftResetTipCount(position=6)
softLinx.conditional(
    conditionalStatement="[SoftLinx.PlateCrane].Speed > 0",
    branchTrue=[
        softLinx.plateCraneMoveCrane("SoftLinx.PlateCrane.Safe", inplace=False)
    ],
    branchFalse=[
        softLinx.plateCraneMovePlate(["SoftLinx.PlateCrane.Home"], inplace=False)
    ],
)
softLinx.saveProtocol()
```
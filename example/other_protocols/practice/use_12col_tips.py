from liquidhandling import SoftLinx, SoloSoft

soloSoft = SoloSoft(
    filename="use_12col_tips.hso",
    plateList=[
        "TipBox.200uL.Corning-4864.orangebox",
        "Empty",
        "Empty",
        "Empty",
        "Empty",
        "Empty",
        "Empty",
        "Empty",
    ],
)

for i in range(1, 13):
    soloSoft.getTip()

soloSoft.shuckTip()
soloSoft.savePipeline()

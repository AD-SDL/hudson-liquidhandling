"""
SoftLinx protocol to test tip replacement

TODO: put this code into a method that can be called when tip box is flagged as empty?
NOTE: Hudson needs to update SoftLinx/SoloSoft before TipCounts conditional is usable

PLATE DEFINITIONS USED:
TipBox.200uL.Corning-4864.orangebox
TipBox.50uL.Axygen-EV-50-R-S.tealbox

"""
from liquidhandling import SoloSoft, SoftLinx

# empty_tip_location = "Position6"
# empty_tip_type = "TipBox.50uL.Axygen-EV-50-R-S.tealbox.empty"
# full_tip_type = "TipBox.50uL.Axygen-EV-50-R-S.tealbox"

# empty_tip_stack_location = "Stack5"
# full_tip_stack_location = "Stack4"

# softLinx = SoftLinx("Tip Replacement Test", "tip_replacement_test.slvp")
# softLinx.setPlates({"SoftLinx.PlateCrane." + full_tip_stack_location: full_tip_type, "SoftLinx.Solo." + empty_tip_location: empty_tip_type})

# # remove the empty plate and place it in an empty stack locaiton
# softLinx.plateCraneMovePlate(["SoftLinx.Solo." + empty_tip_location], ["SoftLinx.PlateCrane." + empty_tip_stack_location])

# # pick up the new tip box and place it in the correct location
# softLinx.plateCraneMovePlate(["SoftLinx.PlateCrane." + full_tip_stack_location], ["SoftLinx.Solo." + empty_tip_location])

# softLinx.saveProtocol()

# --------------------------------------------------------------------------------------------------------------
# default_empty_tip = "TipBox.50uL.Axygen-EV-50-R-S.tealbox.empty"
tip_box_name = "TipBox.200uL.Corning-4864.orangebox"
default_empty_tip_loc = "SoftLinx.Solo.Position6"
default_empty_tip_storage = "SoftLinx.PlateCrane.Stack5"
default_full_tip_storage = "SoftLinx.PlateCrane.Stack4"

# previously instantiated SoftLinx
softLinx = SoftLinx("Tip Replacement Test Main", "tip_replacement_test_main.slvp")
softLinx.setPlates(
    {
        default_full_tip_storage: tip_box_name,
        default_empty_tip_loc: tip_box_name,
    }
)

# Replace Tips Method ----------------------------------------------------------------
def replace_tips(
    current_softLinx,  # required argument! -> can't run multiple .slvp files
    empty_tip_location,  # "Position6" -> "SoftLinx.Solo.Position6"
    empty_tip_storage="SoftLinx.PlateCrane.Stack4",
    full_tip_storage="SoftLinx.PlateCrane.Stack5",
):
    print("Now replacing the tips")
    print("\tempty tip location -> " + empty_tip_location)
    print("\tempty tip storage -> " + empty_tip_storage)
    print("\tfull tip storage -> " + full_tip_storage)

    # format empty tip location and determine tip type at that location
    empty_tip_location = "SoftLinx.Solo." + str(empty_tip_location)
    print("Empty tip location: " + str(empty_tip_location))
    tip_type = current_softLinx.plates[empty_tip_location]
    print("Tip type: " + str(tip_type))

    # remove the empty plate and place it in an empty stack locaiton
    current_softLinx.plateCraneMovePlate(
        [empty_tip_location],
        [empty_tip_storage],
        # hasLid = False <-- default setting
    )

    # pick up the new tip box and place it in the correct location
    current_softLinx.plateCraneMovePlate(
        [full_tip_storage],
        [empty_tip_location],
        hasLid=True,
    )
    # softLinx.saveProtocol()


# ---------------------------------------------------------------------------------------------------

# * Use all tips in a tip box
softLinx.soloSoftResetTipCount(6)  # automatically reset the tip count (for testing)
soloSoft = SoloSoft(
    filename="use_all_tips.hso",
    plateList=[
        "Empty",
        "Empty",
        "Empty",
        "Empty",
        "Empty",
        "TipBox.200uL.Corning-4864.orangebox",
        "Empty",
        "Empty",
    ],
)

for i in range(1, 13):
    soloSoft.getTip("Position6")
soloSoft.shuckTip()
soloSoft.savePipeline()

# * Test conditional recognition of empty tip box
# softLinx.conditional(
#     conditionalStatement="[SoftLinx.PlateCrane].Speed > 0",
#     branchTrue=[
#         softLinx.plateCraneMoveCrane("SoftLinx.PlateCrane.Safe", inplace=False)
#     ],
#     branchFalse=[
#         softLinx.plateCraneMovePlate(["SoftLinx.PlateCrane.Home"], inplace=False)
#     ],
# )

softLinx.conditional(conditionalStatement="[SoftLinx.Solo].TipCount")

# add conditional here
replace_tips(current_softLinx=softLinx, empty_tip_location="Position6")


softLinx.saveProtocol()

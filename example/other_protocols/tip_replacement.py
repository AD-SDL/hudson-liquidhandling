"""
SoftLinx protocol to test tip replacement

TODO: put this code into a method that can be called when tip box is flagged as empty?

PLATE DEFINITIONS USED:
TipBox.200uL.Corning-4864.orangebox
TipBox.200uL.Corning-4864.orangebox.empty

TipBox.50uL.Axygen-EV-50-R-S.tealbox
TipBox.50uL.Axygen-EV-50-R-S.tealbox.empty

"""
from liquidhandling import SoftLinx

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


default_empty_tip = "TipBox.50uL.Axygen-EV-50-R-S.tealbox.empty"
default_full_tip = "TipBox.50uL.Axygen-EV-50-R-S.tealbox"
default_empty_tip_loc = "SoftLinx.Solo.Position6"
default_empty_tip_storage = "SoftLinx.PlateCrane.Stack5"
default_full_tip_storage = "SoftLinx.PlateCrane.Stack4"

# do i need to include self as a paramater if method does not yet blong to a class?
def replace_tips(
    empty_tip_type=default_empty_tip,
    full_tip_type=default_full_tip,
    empty_tip_location=default_empty_tip_loc,
    empty_tip_storage=default_empty_tip_storage,
    full_tip_storage=default_full_tip_storage,
):
    print("Now replacing the tips")
    print("\tempty tip type -> " + empty_tip_type)
    print("\tfull tip type -> " + full_tip_type)
    print("\tempty tip location -> " + empty_tip_location)
    print("\tempty tip storage -> " + empty_tip_storage)
    print("\tfull tip storage -> " + full_tip_storage)

    # do we assume that softLinx is alredy initialized wherever this code is happening? --> for now no

    softLinx = SoftLinx("Tip Replacement Test", "tip_replacement_test.slvp")
    softLinx.setPlates(
        {
            "SoftLinx.PlateCrane." + full_tip_storage: full_tip_type,
            "SoftLinx.Solo." + empty_tip_location: empty_tip_type,
        }
    )

    # remove the empty plate and place it in an empty stack locaiton
    softLinx.plateCraneMovePlate(
        ["SoftLinx.Solo." + empty_tip_location],
        ["SoftLinx.PlateCrane." + empty_tip_storage],
    )

    # pick up the new tip box and place it in the correct location
    softLinx.plateCraneMovePlate(
        ["SoftLinx.PlateCrane." + full_tip_storage],
        ["SoftLinx.Solo." + empty_tip_location],
    )

    softLinx.saveProtocol()

replace_tips()

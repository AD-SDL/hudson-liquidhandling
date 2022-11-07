from liquidhandling import SoloSoft, SoftLinx
from liquidhandling import *


tip_box_name = "TipBox.180uL.Axygen-EVF-180-R-S.bluebox"
default_empty_tip_loc = "SoftLinx.Solo.Position3"
default_empty_tip_storage = "SoftLinx.PlateCrane.Stack4"
default_full_tip_storage = "SoftLinx.PlateCrane.Stack3"

softLinx = SoftLinx("Tip To Deck Loop TEST", "tip_to_deck_loop_TEST.slvp")

softLinx.setPlates(
    {
        default_full_tip_storage: tip_box_name,
        default_empty_tip_loc: tip_box_name,
    }
)

softLinx.plateCraneMovePlate([default_full_tip_storage], [default_empty_tip_loc])
softLinx.liconicShake()
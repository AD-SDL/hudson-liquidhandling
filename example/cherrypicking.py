from liquidhandling import CherryPicking
from liquidhandling import GenericPlate96Well

cherryPicking = CherryPicking(
    # Using the Dictionary-style pick list, but there are 2 others
    pickList={"A1": [("A1", 10), ("A2", 5), ("A3", 1)], "B2": [("C1", 20), ("E5", 10)]},
    plateList=[
        "TipBox-Corning 200uL",
        "Corning 3383",
        "Corning 3383",
        "Corning 3383",
        "Corning 3383",
        "Corning 3383",
        "Corning 3383",
        "Corning 3383",
    ],
    filename_prefix="cherry_pick_",
    source_plate_position="Position6",
    source_plate_type=GenericPlate96Well,
    destination_plate_position="Position7",
    destination_plate_type=GenericPlate96Well,
)

pick_protocols = cherryPicking.generateCherryPicking(
    tipbox_position="Position3",
    get_tips_between_sources=False,
    max_aspirate=50,
    aspirate_options={"mix_at_start": True, "mix_cycles": 3, "mix_volume": 10},
    dispense_options={"blowoff": 2},
)

for protocol in pick_protocols:
    protocol.savePipeline()

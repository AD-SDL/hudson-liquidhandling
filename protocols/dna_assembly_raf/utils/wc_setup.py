from liquidhandling import SoftLinx
from .tip_utils import replace_tip_box

# HELPER METHODS: ---------------------------------------------------------------
def set_up(
    current_softLinx:SoftLinx, 
    incubator_plate_id, 
    empty_tip_deck_loc,
    new_tip_storage_loc="SoftLinx.PlateCrane.Stack4",
): 
    """ set_up

        Descrition: Sets up SOLO deck for liquidhandling
                    Retreives specified plate from incubator and places it on SOLO position 6
                    Retreives prefilled LB plate from Stack5 and places it on SOLO position 4

        Parameters: 
            current_softLinx: the instance of SoftLinx that should add the included steps
            incubator_plate_id: plate_id corresponding to incubaotor plate to place on SOLO deck
            empty_tip_deck_loc: TODO
            new_tip_storage_loc: TODO
            
    """
    # place new tip box on the deck
    replace_tip_box(
        current_softLinx=current_softLinx, 
        empty_tip_loc=empty_tip_deck_loc, 
        full_tip_storage=new_tip_storage_loc, 
        poolID=4,  # pool id = stack num
    )  

    # place plate from incubator on deck, remove lid
    current_softLinx.liconicUnloadIncubator(loadID=incubator_plate_id)
    current_softLinx.plateCraneMovePlate(["SoftLinx.Liconic.Nest"],["SoftLinx.Solo.Position6"])  
    current_softLinx.plateCraneRemoveLid(["SoftLinx.Solo.Position6"],["SoftLinx.PlateCrane.LidNest1"])

    # place prefilled media plate onto solo deck position 4, remove lid
    current_softLinx.plateCraneMovePlate(["SoftLinx.PlateCrane.Stack5"],["SoftLinx.Solo.Position4"], poolID=5)  # pool id = stack num
    current_softLinx.plateCraneRemoveLid(["SoftLinx.Solo.Position4"],["SoftLinx.PlateCrane.LidNest2"])

    current_softLinx.plateCraneMoveCrane("SoftLinx.PlateCrane.Safe")


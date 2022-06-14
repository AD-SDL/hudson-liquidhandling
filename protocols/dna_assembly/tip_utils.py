def replace_tip_box(
    current_softLinx,
    empty_tip_loc,  
    full_tip_storage="SoftLinx.PlateCrane.Stack4",
    poolID=4,
): 
    """ replace_tip_box

    Description: TODO

    Parameters: 
        current_softLinx: TODO
        empty_tip_loc: TODO
        full_tip_storage: TODO
        pool_id: TODO

    """
    empty_tip_loc = "SoftLinx.Solo." + str(empty_tip_loc)

      # pick up the new tip box and place it in the correct location
    current_softLinx.plateCraneMovePlate(
        [full_tip_storage],
        [empty_tip_loc],
        hasLid=True,
        poolID=poolID,  # TODO check this
    )

    # move crane to safe 
    current_softLinx.plateCraneMoveCrane("SoftLinx.PlateCrane.Safe")

    # reset the tip count for location of new tip box
    current_softLinx.soloSoftResetTipCount(int(empty_tip_loc[-1]))  


# --------------------------------------------------------------------------------------------
def remove_tip_box(
    current_softLinx,
    empty_tip_loc, 
    empty_tip_storage="SoftLinx.PlateCrane.Stack3",
    poolID=3, 
):
    """ remove_tip_box

    Description: TODO 

    Parameters: 
        current_softLinx: TODO
        empty_tip_location: TODO
        empty_tip_storage: TODO

    """
    empty_tip_loc = "SoftLinx.Solo." + str(empty_tip_loc)

    # remove the empty plate and place it in an empty stack locaiton
    current_softLinx.plateCraneMovePlate(
        [empty_tip_loc],
        [empty_tip_storage],
        hasLid=False,
        poolID=poolID,
    )

    # move crane to safe 
    current_softLinx.plateCraneMoveCrane("SoftLinx.PlateCrane.Safe")
    


def replace_tip_box(
    current_softLinx,
    empty_tip_location,  
    full_tip_storage="SoftLinx.PlateCrane.Stack4",
): 

    empty_tip_location = "SoftLinx.Solo." + str(empty_tip_location)
    # tip_type = current_softLinx.plates[empty_tip_location]

      # pick up the new tip box and place it in the correct location
    current_softLinx.plateCraneMovePlate(
        [full_tip_storage],
        [empty_tip_location],
        hasLid=True, poolID=4
    )

def remove_tip_box(
    current_softLinx,
    empty_tip_location, 
    empty_tip_storage="SoftLinx.PlateCrane.Stack3", 
):

    empty_tip_location = "SoftLinx.Solo." + str(empty_tip_location)

    # remove the empty plate and place it in an empty stack locaiton
    current_softLinx.plateCraneMovePlate(
        [empty_tip_location],
        [empty_tip_storage],
        poolID=3
    )
    


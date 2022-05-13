# ---------------------------------------------------------------------------------
def tear_down(
    current_softLinx:SoftLinx, 
    incubator_plate_id, 
    incubation_time, 
    shaker_speed=30, 
    empty_tip_deck_loc="Position3", 
    empty_tip_storage_loc="SoftLinx.PlateCrane.Stack3",
): 
    """ tear_down
    
        Description: Clears the SOLO deck after liquidhandling is complete
                     Transfers the plate into the incubator

        Parameters:
            current_softLinx: the instance of SoftLinx that should add the included steps
            incubator_plate_id: plate_id of the newly completed plate to be placed in incubator
            incubation_time: How long the plate should incubate before next step of the protocol 
                note: must be a list of integers [days, hours, minutes, seconds] (ex. [0,3,0,0] means 3 hours)
            shaker_speed: shaker setting for incubator. Must be 1-50. (20 = 200 rpm, 30 = 300 rpm, etc.)
            empty_tip_deck_loc: TODO 
            empty_tip_storage_loc: TODO
    
    """
    # remove used tip box from deck
    remove_tip_box(
        current_softLinx=current_softLinx, 
        empty_tip_loc=empty_tip_deck_loc, 
        empty_tip_storage=empty_tip_storage_loc, 
        poolID=3, # pool id = stack num
    )  

    # remove used origin plate from deck and place in stack 1
    current_softLinx.plateCraneReplaceLid(["SoftLinx.PlateCrane.LidNest1"], ["SoftLinx.Solo.Position6"])
    current_softLinx.plateCraneMovePlate(["SoftLinx.Solo.Position6"], ["SoftLinx.PlateCrane.Stack1"], poolID=1)

    # replace lid on new plate and move to incubator nest 
    current_softLinx.plateCraneReplaceLid(["SoftLinx.PlateCrane.LidNest2"], ["SoftLinx.Solo.Position4"])
    current_softLinx.plateCraneMovePlate(["SoftLinx.Solo.Position4"],["SoftLinx.Liconic.Nest"])
    current_softLinx.plateCraneMoveCrane("SoftLinx.PlateCrane.Safe")

    # load the new plate into the incubator
    current_softLinx.liconicLoadIncubator(loadID=incubator_plate_id)
    current_softLinx.liconicShake(shaker1Speed=shaker_speed, shakeTime=incubation_time)

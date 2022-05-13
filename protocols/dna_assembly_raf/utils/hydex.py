def take_hidex_reading(current_softLinx:SoftLinx, directory_name, incubator_plate_id, hidex_assay): 
    """ take_hidex_reading

        Description: Removes the specified plate (plate_id) from incubator and transfers to Hidex
                     Runs desired Hidex assay (hidex_assay) to collect data on plate
                     Transfers data file to lambda6 for data processing

        Parameters: 
            current_softLinx: the instance of SoftLinx that should add the included steps
            incubator_plate_id: plate_id of the newly completed plate to be placed in incubator
            hidex_assay: string name of assay protocol name on Hidex app (on hudson01) that you wish to run

    """
    # remove specified plate from incubator
    current_softLinx.liconicUnloadIncubator(loadID=incubator_plate_id)

    # remove lid and transfer to Hidex
    current_softLinx.plateCraneRemoveLid(["SoftLinx.Liconic.Nest"],["SoftLinx.PlateCrane.LidNest2"])
    current_softLinx.plateCraneMovePlate(["SoftLinx.Liconic.Nest"],["SoftLinx.Hidex.Nest"])
    current_softLinx.plateCraneMoveCrane("SoftLinx.PlateCrane.Safe")

    # take Hidex reading
    current_softLinx.hidexRun("SetTempWait37")  # make sure hidex is at 37C  # TODO: combine into one Hidex protocol 
    current_softLinx.hidexRun(hidex_assay)

    # transfer data to lambda6
    data_format = "dna_assembly"
    current_softLinx.runProgram(   
        "C:\\Users\\svcaibio\\Dev\\liquidhandling\\zeromq\\utils\\send_data.bat", 
        arguments=f"{incubator_plate_id} {directory_name} {data_format}"
    )
BATS/dALE Putida.OD600 Protocols 

DECK LAYOUT:
    1 -> TipBox.200uL.Corning-4864.orangebox
    2 -> Empty (HEATING NEST)
    3 -> Reservoir.12col.Agilent-201256-100.BATSgroup
            (Water -> Columns 1 & 2; Buffer -> Columns 7 & 8)
    4 -> Plate.96.Agilent-5043-9310.RoundBottomStorage
    5 -> DeepBlock.96.VWR-75870-792.sterile
    6 -> Plate.96.Corning-3635.ClearUVAssay
    7 -> Plate.96.PlateOne-1833-9600.ConicalBottomStorage
    8 -> Empty

HOW TO RUN THESE PROTOCOLS:
    If you prefer to use SoloSoft .hso protocols:
        (Premade SoloSoft protocols for all steps can be found in the premade_hso_files folder)
        NOTE: premadefiles only appear in repo on hudson01, git ignores .hso files
        - Open SoloSoft from the Desktop
        - Open the .hso file you wish to use and run it, all from within the SoloSoft application

    If you prefer to use SoftLinx:
        - make sure that you cd into the correct folder...
           'cd C:\Users\svcaibio\Dev\liquidhandling\example\BATS\dALE'
        - run the python file corresponding to the step you wish to run 
            example -> 'python putida_OD600_steps1and2_DispenseAll.py'
        - matching .hso, .slvp, and .hso files will appear in the BATS/dALE folder
            example -> putida_OD600_steps1and2_DispenseAll.hso
                       putida_OD600_steps1and2_DispenseAll.slvp
                       putida_OD600_steps1and2_DispenseAll.ahk
        - Either open the SoftLinxVProtocol Editor from the Desktop and load in the 
          matching .slvp file 
          ...OR...
          Make sure that all SoftLinx and SoloSoft programs are closed and double click 
          on the .ahk file
            - this will automatically open SoftLinx and run the protocol

DESCRIPTION OF EACH PROTOCOL:
putida_OD600_DispenseWater.py
- Transfer 180uL water from 12 Channel Reservoir - Column 1 to ClearUVAssay - Columns 1-6
- Transfer 180 uL water from 12 Channel Reservoir - Column 2 to ClearUVAssay - Columns 7-12

putida_OD600_DispenseBuffer.py
- Transfer 180uL buffer from 12 Channel Reservoir - Column 7 to Round Bottom Storage - Columns 1-6
- Transfer 180uL buffer from 12 Channel Reservoir - Column 8 to Round Bottom Storage - Columns 7-12

putida_OD600_steps1and2_DispenseAll.py
    Combines both above dispense protocols into one protocol. 

putida_OD600_step3_TransferBacteria.py
- Transfer 20uL bacterial suspension from DeepBlock - Columns 1-12 to ClearUVAssay - Columns 1-12  
    - uses 200uL tips 
    - keeps 3 mm clearance from the bottom of wells

putida_OD600_step4_ClearUVToPlateOneVBottom.py
- Transfer 150uL of availible 200uL from all wells in ClearUVAssay plate to 
  all wells in  ConicalBottomStorage

putida_OD600_step5_TransferToRoundBottom.py
- Transfer 20uL supernatant from ConicalBottomStorage - Columns 1-12 to 
  RoundBottomStorage - Columns 1-12 
    - 2mm clearance from the bottom
    - 2mm x and y shift during aspiration


        

          
                    

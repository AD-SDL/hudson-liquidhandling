# DNA ASSEMBLY PROTOCOL

## Running

  python run_protocol.py --is_test True
 
## Workcell 

SOLO DECK ARRANGEMENT AT START: 
Pos 1 = EMPTY
Pos 2 = EMPTY (heat nest)
Pos 3 = 50uL tips (filter tips if possible)
Pos 4 = EMPTY AT START (later 96 well clear, flat-bottom plate w/ lid placed by Plate Crane)
Pos 5 = EMPTY
Pos 6 = EMPTY AT START (later 96 well clear, flat-bottom plate w/ lid placed by Plate Crane)
Pos 7 = EMPTY
Pos 8 = EMPTY

POST TRANSFORMATION STEPS: 
*** start with transformation plate in incubator, with incubator plate ID = 1 ***

Transformation plate to selection plate #1 
- Unload transformation plate from incubator --> SOLO position 6
- Move new plate to SOLO position 4 (will be selection plate #1)
    Note: new plate will contain 180uL LB media + antobiotic in each well)
- exectue transf_to_sel.hso: 
    - transfer 10uL from each well of transformation plate to corresponding well in selection plate #1 
- Load selection plate #1 into incubator (plate ID = 2) and remove used transformation plate to Stack 1
- Incubate for 3 hours

Selection plate #1 to master plate:
- Unload selection plate #1 from incubator (plate ID = 2) --> SOLO position 6
- Move new plate to SOLO position 4 (will be master plate)
    (Note: new plate will contain 100uL of 50% glycerol media in each well)
- exectue sel_to_master.hso: 
    - transfer 100uL from each well of selection plate #1 to corresponding well in master plate  
- Load master plate into incubator, plate ID = 3
- Freeze for later use or immediately proceed to next step 
    (If proceeding, remove used selection plate #1 to Stack 1 and move master plate to SOLO position 6)

Master plate to overnight plate: 
- Unload master plate from incubator (plate ID = 3) --> SOLO position 6
- Move new plate to SOLO position 4 (will be overnight plate)
    (Note: new plate will contain 180uL LB media + antibiotic in each well)
- exectue master_to_overnight.hso: 
    - transfer 10uL from each well of master plate to corresponding well in overnight plate 
- Load overnight plate into incubator, plate ID = 4
- Incubate for 8 hours

Overnight plate to test plate: 
- Unload overnight plate from incubator (plate ID = 4) --> SOLO position 6
- Move new plate to SOLO position 4 (will be test plate)
    (Note: new plate will contain 180uL LB media + antibiotic in each well)
- exectue overnight_to_test.hso: 
    - transfer 10uL from each well of overnight plate to corresponding well in test plate 

Take Hidex Readings: 
START LOOP (6 times)
- Move test plate to Hidex (either move from SOLO Position 4 or unload from incubator)
- Run Hidex Assay 
    - TODO: details about assay
- Load test plate into incubator (except after last reading move to Stack 1)
- Incubate for 1 hour
END LOOP

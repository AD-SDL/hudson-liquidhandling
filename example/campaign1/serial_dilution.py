"""
CUSTOMIZABLE SERIAL DILUTION PROTOCOL

#TODO Documentation

"""

import os
import sys

#* Program Variables --------------------------------------------------------------------------------
# TODO: clean up this section

dilution_method_number = 3
output_hso_filename = "serial_dilution_test1.hso"
num_columns = 4  # required by both variable options
desired_final_volume = 100  #measured in microliters

num_mixes = 5
blowoff_volume = 20
stock_mix_volume = 50   # TODO: Calculate these mix volumes based on total volume after calculations
dilution_mix_volume = 50 


# METHOD 1 VARIABLES
highest_concentration = 1/1000
lowest_concentration = 1/16000

# METHOD 2 VARIABLES
dilution_factor = 1/10 # example -> 2 means 2-fold dilution (df = 1/2)

# METHOD 3 VARIABLES
    # also uses highest concentration variable in method 1 variables
dilution_concentrations_list = [1/2000, 1/4000, 1/40000]

# Plate location varibales #TODO decide what these defaults should be later 
# dilution_plate_nest_num = 1
# dilution_plate_type = "Corning 3383"  # for now Corning 3383 is the default 

# stock_solution_nest_num = 4
stock_solution_column_num = 2 # might not need this
# stock_solution_plate_type = "12 Channel Reservoir"

# diluent_nest_num = 4
diluent_column_num = 1 
# diluent_plate_type = "12 Channel Reservoir"

#* create the plate list from plate location/type variables --------------------------------------------
# plate_list = ["Empty"]*8
# for i in range (1,9):
#     if dilution_plate_nest_num == i:
#         plate_list[i-1] = dilution_plate_type
#     elif stock_solution_nest_num == i:
#         plate_list[i-1] = stock_solution_plate_type
#     elif diluent_nest_num == i:
#         plate_list[i-1] = diluent_plate_type
# -----------------------------------------------------------------------------------------------------


# TODO: see Tom's note on slack in testing channel
# Change this path to point to the location of the repository, if neccessary
sys.path.append(
    os.path.abspath(
        os.path.join(os.path.abspath(os.path.dirname(__file__)), "../../src")
    )
)
import SoloSoft

from Plates import (  # TODO: figure out how to import the right plates based on user plate specificaitons 
    GenericPlate96Well,
    NinetySixDeepWell,
    ZAgilentReservoir_1row,
) 

soloSoft = SoloSoft.SoloSoft(
    filename=output_hso_filename,
    plateList=[
        "TipBox-Corning 200uL",
        "Empty",
        "Corning 3383",
        "Corning 3383",
        "12 Channel Reservoir",
        "Empty",
        "Empty",
        "Empty",
    ],
)

#* CALCULATIONS ------------------------------------------------------------------------

#* Method 1
if dilution_method_number == 1:
    dilution_factor = (lowest_concentration/highest_concentration) ** (1/num_columns) # dilution factor
    serial_transfer_volume = dilution_factor * desired_final_volume  # TODO: does this need to be an int? or float? ect. 
    diluent_transfer_volume = desired_final_volume - serial_transfer_volume

#* Method 2
elif dilution_method_number == 2:
    serial_transfer_volume = dilution_factor * desired_final_volume  # TODO: do these need to be an int? or float? ect. 
    diluent_transfer_volume = desired_final_volume - serial_transfer_volume

#* Method 3 
elif dilution_method_number == 3:
    num_columns = len(dilution_concentrations_list)
    serial_transfer_volumes = [0]*num_columns
    diluent_transfer_volumes = [0]*num_columns
    for i in range(len(dilution_concentrations_list)):
        if i == 0: 
            current_dilution_factor = (dilution_concentrations_list[i]/highest_concentration) 
        else:
            current_dilution_factor = (dilution_concentrations_list[i]/dilution_concentrations_list[i-1])
        serial_transfer_volumes[i] = current_dilution_factor * desired_final_volume
        diluent_transfer_volumes[i]  = desired_final_volume - serial_transfer_volumes[i]

#*  GENERATE SOLOSOFT .HSO FILE ---------------------------------------------------------------------------

if dilution_method_number == 1 or dilution_method_number == 2:
    # distribute diluent into all required wells 
    soloSoft.getTip() 
    for i in range(1,num_columns+1):  # maybe add blowoff
        soloSoft.aspirate(  
            position="Position5", 
            aspirate_volumes=ZAgilentReservoir_1row().setColumn(1, diluent_transfer_volume),
            aspirate_shift = [0,0,4] # larger z-shift needed for 12 channel reservoir
        )
        soloSoft.dispense(
            position="Position4",
            dispense_volumes=GenericPlate96Well().setColumn(i+1, diluent_transfer_volume), 
            dispense_shift=[0,0,2], 
        )
    
    # dilute into first column from stock solution
    soloSoft.aspirate(
        position="Position3", 
        aspirate_volumes=GenericPlate96Well().setColumn(1, serial_transfer_volume),  # TODO make sure the user places stock solution in this location
        aspirate_shift = [0,0,2], 
        mix_at_start=True,
        mix_cycles=num_mixes,
        mix_volume=stock_mix_volume,
        dispense_height=2,
    )
    soloSoft.dispense(
        position="Position4",
        dispense_volumes=GenericPlate96Well().setColumn(1, serial_transfer_volume), 
        dispense_shift=[0,0,2], 
        mix_at_finish=True, 
        mix_cycles=num_mixes, 
        mix_volume=dilution_mix_volume,
        aspirate_height=2,
    )

    # serial dilute into the remaining columns
    for i in range(1,num_columns):  
        soloSoft.aspirate(
            position="Position4", 
            aspirate_volumes=GenericPlate96Well().setColumn(i, serial_transfer_volume),  # TODO make sure the user places stock solution in this location
            aspirate_shift = [0,0,2], 
            mix_at_start=True,
            mix_cycles=num_mixes,
            mix_volume=stock_mix_volume,
            dispense_height=2,
        )
        soloSoft.dispense(
            position="Position4",
            dispense_volumes=GenericPlate96Well().setColumn(i+1, serial_transfer_volume), 
            dispense_shift=[0,0,2], 
            mix_at_finish=True, 
            mix_cycles=num_mixes, 
            mix_volume=dilution_mix_volume,
            aspirate_height=2,
        )

    soloSoft.shuckTip()
    soloSoft.savePipeline()

elif dilution_method_number == 3: 

    # dispense predetermined differing amounts of diluent to each well
    soloSoft.getTip()
    for i in range(1,num_columns+1):
        soloSoft.aspirate(
            position="Position5", 
            aspirate_volumes=ZAgilentReservoir_1row().setColumn(1, diluent_transfer_volumes[i-1]),
            aspirate_shift=[0,0,4],
        )
        soloSoft.dispense(
            position="Position3", 
            dispense_volumes=GenericPlate96Well().setColumn(i, diluent_transfer_volumes[i-1]), 
            dispense_shift=[0,0,2],
        )

    # dispense the predetermined correct amount of stock solution into the first column
    soloSoft.aspirate(
        position="Position3", 
        aspirate_volumes=GenericPlate96Well().setColumn(1, serial_transfer_volumes[0]),  # TODO make sure the user places stock solution in this location
        aspirate_shift = [0,0,2], 
        mix_at_start=True,
        mix_cycles=num_mixes,
        mix_volume=stock_mix_volume,
        dispense_height=2,
    )
    soloSoft.dispense(
        position="Position4",
        dispense_volumes=GenericPlate96Well().setColumn(1, serial_transfer_volumes[0]), 
        dispense_shift=[0,0,2], 
        mix_at_finish=True, 
        mix_cycles=num_mixes, 
        mix_volume=dilution_mix_volume,
        aspirate_height=2,
    )

    # serial dilute into remaining columns 
    for i in range(1,num_columns):  
        soloSoft.aspirate(
            position="Position4", 
            aspirate_volumes=GenericPlate96Well().setColumn(i, serial_transfer_volumes[i-1]),  # TODO make sure the user places stock solution in this location
            aspirate_shift = [0,0,2], 
            mix_at_start=True,
            mix_cycles=num_mixes,
            mix_volume=stock_mix_volume,
            dispense_height=2,
        )
        soloSoft.dispense(
            position="Position4",
            dispense_volumes=GenericPlate96Well().setColumn(i+1, serial_transfer_volumes[i-1]), 
            dispense_shift=[0,0,2], 
            mix_at_finish=True, 
            mix_cycles=num_mixes, 
            mix_volume=dilution_mix_volume,
            aspirate_height=2,
        )

    soloSoft.shuckTip()
    soloSoft.savePipeline()



        




    



    











    

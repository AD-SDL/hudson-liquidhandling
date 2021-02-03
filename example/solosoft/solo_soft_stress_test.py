import sys
import json
import jsonref
import os
from jsonschema import validate
from liquidhandling import SoloSoft
from liquidhandling import GenericPlate96Well

# Validate our pipeline using JSON schema for reference
def validate_pipeline():
    jsonified_pipeline = soloSoft.pipelineToJSON()
    current_directory = os.path.abspath(os.path.dirname(__file__))
    schema_file_path = os.path.join(
        current_directory, "../../src/json_schema/SoloSoft/pipeline.json"
    )
    json_schema_path = os.path.join(current_directory, "../../src/json_schema/SoloSoft")

    if os.name == "nt":
        base_uri = "file:///{}/".format(json_schema_path)
    else:
        base_uri = "file://{}/".format(json_schema_path)

    with open(os.path.join(os.path.dirname(__file__), "test.json"), "w") as f:
        json.dump(jsonified_pipeline, f, indent=4, sort_keys=True)

    with open(schema_file_path) as schema_file:
        my_schema = jsonref.load(schema_file, base_uri=base_uri, jsonschema=True)

        validate(instance=jsonified_pipeline, schema=my_schema)


# Initialize Pipeline
soloSoft = SoloSoft.SoloSoft(
    filename="stress_test.hso",
    plateList=[
        "TipBox-200uL Corning 4864",
        "TipBox-50uL EV-50-R-S",
        "TipBox-50uL EV-50-R-S",
        "Empty",
        "Empty",
        "Agilent 12 Channel Reservoir (#201256-100) ",
        "Omni",
        "Falcon 353916- round 96",
    ],
)

# Main sequence of steps that we need to repeat across multiple rows
def sub_pipeline(i, interim_get_tips=False, interim_pause=False):
    soloSoft.getTip(position="Position2")
    soloSoft.aspirate(
        position="Position8",
        aspirate_shift=[0, 0, 0.2],
        syringe_speed=50,
        mix_at_start=True,
        mix_cycles=5,
        mix_volume=30,
        dispense_height=2,
        post_aspirate=1,
        aspirate_volumes=GenericPlate96Well().setColumn(i, 10),
    )
    soloSoft.dispense(
        position="Position8",
        dispense_shift=[0, 0, 0.2],
        syringe_speed=50,
        mix_at_finish=True,
        mix_cycles=5,
        mix_volume=50,
        aspirate_height=0.5,
        dispense_volumes=GenericPlate96Well().setColumn(i + 1, 10),
    )
    if interim_pause:
        soloSoft.pause(allow_end_run=True, pause_message="finished first half")
    if interim_get_tips:
        soloSoft.getTip(position="Position2")
    soloSoft.aspirate(
        position="Position8",
        aspirate_shift=[0, 0, 0.5],
        syringe_speed=100,
        aspirate_volumes=GenericPlate96Well().setColumn(i, 3.5),
    )
    soloSoft.dispense(
        position="Position7",
        dispense_shift=[0, 0, 0.5],
        syringe_speed=100,
        dispense_volumes=GenericPlate96Well().setColumn(i, 3.5),
    )


# Generate Pipeline
for i in range(1, 12):
    if i == 1:
        sub_pipeline(i, True)
    elif i == 6:
        sub_pipeline(i, True, True)
    else:
        sub_pipeline(i)
soloSoft.getTip(position="Position2")
soloSoft.aspirate(
    position="Position8",
    aspirate_shift=[0, 0, 0.5],
    syringe_speed=100,
    aspirate_volumes=GenericPlate96Well().setColumn(12, 3.5),
)
soloSoft.dispense(
    position="Position7",
    dispense_shift=[0, 0, 0.5],
    syringe_speed=100,
    dispense_volumes=GenericPlate96Well().setColumn(12, 3.5),
)
soloSoft.shuckTip()
validate_pipeline()
soloSoft.savePipeline()

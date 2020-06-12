import sys
import json
import jsonref
import os
from json import dump
import errno
from jsonschema import validate

# Change this path to point to the location of the repository, if neccessary
sys.path.append(
    os.path.abspath(os.path.join(os.path.abspath(os.path.dirname(__file__)), "../src"))
)
import SoloSoft
from Plates import Plate96Well

soloSoft = SoloSoft.SoloSoft(
    filename="agilent_rese.hso",
    plateList=[
        "TipBox-Corning 200uL",
        "Corning 3383",
        "Corning 3383",
        "Corning 3383",
        "Corning 3383",
        "Z_Agilent_Reservoir_1row",
        "Corning 3383",
        "Corning 3635",
    ],
)

soloSoft.loop(6)
soloSoft.getTip()
# Add 6 aspirate/dispense cycles
for i in range(1, 7):
    soloSoft.aspirate(
        position="Position6",
        aspirate_shift=[0, 0, 2],
        aspirate_volumes=Plate96Well().setColumn(6, 180),
    )
    soloSoft.dispense(
        position="Position8",
        dispense_shift=[0, 0, 2],
        dispense_volumes=Plate96Well().setColumn(i, 180),
    )
soloSoft.shuckTip()
soloSoft.getTip()
# Add 6 aspirate/dispense cycles
for i in range(1, 7):
    soloSoft.aspirate(
        position="Position6",
        aspirate_shift=[0, 0, 2],
        aspirate_volumes=Plate96Well().setColumn(8, 180),
    )
    soloSoft.dispense(
        position="Position8",
        dispense_shift=[0, 0, 2],
        dispense_volumes=Plate96Well().setColumn(i + 6, 180),
    )
soloSoft.shuckTip()
soloSoft.pause(
    pause_message="Finished plate. Reload buffers and destination plate. Please give me a break, humans!",
    allow_end_run=True,
)
soloSoft.endLoop()
soloSoft.moveArm()

jsonified_pipeline = soloSoft.pipelineToJSON()
current_directory = os.path.abspath(os.path.dirname(__file__))
schema_file_path = os.path.join(
    current_directory, "../src/json_schema/SoloSoft/pipeline.json"
)
json_schema_path = os.path.join(current_directory, "../src/json_schema/SoloSoft")

if os.name == "nt":
    base_uri = "file:///{}/".format(json_schema_path)
else:
    base_uri = "file://{}/".format(json_schema_path)

with open(os.path.join(os.path.dirname(__file__), "test.json"), "w") as f:
    json.dump(jsonified_pipeline, f, indent=4, sort_keys=True)

with open(schema_file_path) as schema_file:
    my_schema = jsonref.load(schema_file, base_uri=base_uri, jsonschema=True)

    validate(instance=jsonified_pipeline, schema=my_schema)

soloSoft.savePipeline()

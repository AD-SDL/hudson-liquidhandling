# SoloSoft

The library for interfacing with the [Hudson Robotics Solo Liquid Handler](https://hudsonrobotics.com/products/liquid-handling/solo-liquid-handling/) is available in [`SoloSoft.py`](../liquidhandling/hudson/SoloSoft.py).

## To Use

Add the following to the top of your python file or jupyter notebook:

```python
from liquidhandling import SoloSoft
```

## Basic Functionality

The Solo Liquid Handler is controlled by a proprietary Windows software called SoloSOFT, which runs protocols defined in files with the `.hso` file extension, a custom ASCII-text based file specification. `SoloSoft.py` allows users to define these protocols using python code.

SoloSOFT protocols consist of a linear series of steps to be executed by the device (with a start loop and end loop step to allow for repeated sections). There is no support for conditionals, branches or jumps.

The `SoloSoft` class contains methods and members that mimic the functionality provided by SoloSOFT, with some additional utility and helpers functions to provide ease of use.

It should be noted that the SoloSOFT application has memory-related issues and will often crash when opening protocols with ~70+ individual steps. As a result, we recommend breaking very long protocols up into multipls `.hso` files.

## Members

Each of these members can optionally be defined in the constructor, i.e. `SoloSoft(filename="", plateList=[], pipeline=[])`.

* `pipeline`: an internal representation of the protocol being generated, stored as a `List` of `List` objects, where each sub-`List` represents a single step.
* `plateList`: an internal representation of the plate types in each bed position on the Solo's deck.
* `filename`: where the protocol will be written to. We recommend using absolute paths, but relative paths are also supported.


## Methods

### Helper/Utility Functions

* `setFile`
    * `(str) filename`: an absolute or relative path where the `.hso` for the protocol will be saved.
* `setPlates`
    * `(List) plateList`: a list of strings, where each string is the name of a PlateType. Plate Types must be in the SoloSOFT database, and the list should have a number of entries equal to the number of positions on the Solo's working surface. In the case of ANL's setup, this number is 8. Any position that will not have a plate should be filled with the string value `"Empty"`
* `setPipeline`
    * `(List) pipeline`: a List of Lists, where each sublist is an individual step from a SoloSoft pipeline. This List should generally come from another instance of the SoloSoft classes `pipeline` member, or be empty.
* `removeStep`
    * `(integer) position`: Default: -1. The index of the step in the protocol that must be removed. If not provided or set to `-1`, removes the last step from the protocol.
* `savePipeline`
    * `(string) filename`: Default: `None`. The path where the pipeline will be saved. If set to `None` or not specified, the value of `pipeline` in the parent class is used.
    * `(bool) CRLF`: Default: `True`. Whether or not to produce files with a Carriage Return Line Feed. Set to `True` to write a Windows' readable file, or `False` for other operating systems. For protocols intended to be run using SoloSOFT, this should always be set to `True`.
* `pipelineToJSON`
    * `(List) pipeline`: Default: `None`. A list of lists, where each sublist is a protocol step. By default, or when `None` is passed, uses the pipeline currently in the classes' `pipeline` member.
    * `(List) plateList`: Default: `None`. A List of strings, where each value corresponds to the name of a plate type at a position on the deck. By default, or if `None` is passed, uses the `plateList` member of the class.
* `jsonToPipeline`
    * `(string) json_data`: a string formatted JSON object to parse into a pipeline.
    * `(bool) inplace`: Default: `True`. If `True`, this class's `pipeline` member will be replaced with the output of the parsed JSON. Otherwise, the pipeline is simply returned.
### SoloSOFT Protocol Steps

Note: each of the following functions comes with a companion `jsonify...` step, which is used by `jsonToPipeline()` to convert the step into a JSON representation. While they can be used by the user, we recommend using `jsonToPipeline()` for protocol to JSON conversion.

* `getTip`
* `shuckTip`
* `loop`
* `endLoop`
* `aspirate`
* `dispense`
* `prime`
* `pause`
* `getBottom`
* `setSpeed`
* `moveArm`
* `movePlate`
* `operateAccessory`


### NOT IMPLEMENTED

* `HitPicking`: we have a custom implementation of [Cherry Picking](../liquidhandling/hudson/CherryPicking.py), which should be used in place of the `HitPicking` step provided by SOLOSoft.

# Examples and Usage

Basic Example:

```python
import sys
import os
from liquidhandling import SoloSoft

soloSoft = SoloSoft(
    filename="example.hso",
    plateList=[
        "TipBox-Corning 200uL",
        "Corning 3383",
        "Corning 3383",
        "Corning 3383",
        "Corning 3383",
        "Corning 3383",
        "Corning 3383",
        "Corning 3383",
    ],
)

soloSoft.getTip()
soloSoft.loop(1)
soloSoft.aspirate()
soloSoft.dispense()
soloSoft.endLoop()
soloSoft.moveArm()

soloSoft.savePipeline(CRLF=True)
```

Agilent Reservoir Example:

```python
import sys
import json
import jsonref
import os
from json import dump
import errno
from jsonschema import validate
from liquidhandling import SoloSoft
from liquidhandling import GenericPlate96Well

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
        aspirate_volumes=GenericPlate96Well().setColumn(6, 180),
    )
    soloSoft.dispense(
        position="Position8",
        dispense_shift=[0, 0, 2],
        dispense_volumes=GenericPlate96Well().setColumn(i, 180),
    )
soloSoft.shuckTip()
soloSoft.getTip()
# Add 6 aspirate/dispense cycles
for i in range(1, 7):
    soloSoft.aspirate(
        position="Position6",
        aspirate_shift=[0, 0, 2],
        aspirate_volumes=GenericPlate96Well().setColumn(8, 180),
    )
    soloSoft.dispense(
        position="Position8",
        dispense_shift=[0, 0, 2],
        dispense_volumes=GenericPlate96Well().setColumn(i + 6, 180),
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

```
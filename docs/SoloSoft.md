# SoloSoft

The library for interfacing with the [Hudson Robotics Solo Liquid Handler](https://hudsonrobotics.com/products/liquid-handling/solo-liquid-handling/) is available in [`../src/SoloSoft.py`](../src/SoloSoft.py).

## To Use

Add the following to the top of your python file or jupyter notebook:

```
sys.path.append(
    os.path.abspath(os.path.join(os.path.abspath(os.path.dirname(__file__)), "../../src"))
)
import SoloSoft
```

## Basic Functionality

The Solo Liquid Handler is controlled by a proprietary Windows software called SoloSOFT, which runs protocols defined in files with the `.hso` file extension, a custom ASCII-text based file specification. `SoloSoft.py` allows users to define these protocols using python code.

SoloSOFT protocols consist of a linear series of steps to be executed by the device (with a start loop and end loop step to allow for repeated sections). There is no support for conditionals, branches or jumps.

The `SoloSoft` class contains methods and members that mimic the functionality provided by SoloSOFT, with some additional utility and helpers functions to provide ease of use.

## Members

Each of these members can optionally be defined in the constructor, i.e. `SoloSoft(filename="", plateList=[], pipeline=[])`.

* `pipeline`: an internal representation of the protocol being generated, stored as a `List` of `List` objects, where each sub-`List` represents a single step.
* `plateList`: an internal representation of the plate types in each bed position on the Solo's deck.
* `filename`: where the protocol will be written to.


## Methods

### Helper/Utility Functions

* `setFile`
* `setPlates`
* `setPipeline`
* `removeStep`
* `savePipeline`
* `pipelineToJSON`
* `jsonToPipeline`

### SoloSOFT Protocol Steps

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


### NOT IMPLEMENTED

* `HitPicking`
* `OperateAccessory`
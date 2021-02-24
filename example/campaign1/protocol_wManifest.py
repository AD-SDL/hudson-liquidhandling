"""
This is just an example file to test the creation of a manifest file

"""
import time
import datetime
from liquidhandling import SoloSoft, SoftLinx

# remember to import all the plates that you need


manifest_list = []

# generate a Solosoft protocol

# initialise soloSoft with an empty deck and no given file name
soloSoft = SoloSoft(filename="protocol_wManifest.hso")
soloSoft.getTip()  # add items to the soloSoft pipeline
soloSoft.shuckTip()
soloSoft.savePipeline()

softLinx = SoftLinx("Protocol with Manifest", "protocol_wManifest.slvp")

# add each step and add to manifest list if necessary
softLinx.soloSoftRun(
    "C:\\Users\\svcaibio\\Dev\\liquidhandling\\example\\campaign1\\protocol_wManifest.hso"
)
manifest_list.append("protocol_wManifest.hso")

softLinx.plateCraneMovePlate(
    ["SoftLinx.PlateCrane.Stack1"], ["SoftLinx.Solo.Position6"]
)
softLinx.plateCraneMoveCrane("SoftLinx.PlateCrane.Safe")

softLinx.saveProtocol()
manifest_list.append("protocol_wManifest.slvp")
manifest_list.append("protocol_wManifest.ahk")


# create a new manifest file and save name of all necessary files to it
with open("protocol_wManifest.txt", "w+") as manifest_file:
    manifest_file.write(
        str(time.time()) + "\n"
    )  # add the current timestamp to the top of the file -> could fix timestamp issue from campaign 1
    manifest_file.write(str(datetime.datetime.now()) + "\n")
    manifest_file.writelines("\n".join(manifest_list))

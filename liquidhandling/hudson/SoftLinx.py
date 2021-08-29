import os
import xml.etree.ElementTree as ET
import time
import datetime


class SoftLinx:
    def __init__(
        self,
        displayName=None,
        filename=None,
        protocolSteps=None,
        variables=None,
        plates=None,
    ):
        self.displayName = None
        self.filename = None
        self.protocolSteps = []
        self.variables = []
        self.plates = {}
        self.manifest_list = []
        self.plugin_flags = {
            "PlateCrane": False,
            "Plates": False,
            "Solo": False,
            "Hidex": False,
            "RapidPick": False,
            "TorreyPinesRIC20": False,
        }
        self.plugin_reference = {
            "PlateCrane": 0,
            "Plates": 1,
            "Solo": 2,
            "Hidex": 3,
            # "RapidPick": 4,
            # "TorreyPinesRIC20": 5,
        }
        self.plugin_address = {
            "PlateCrane": 4,
            "Plates": 5,
            "Solo": 6,
            "Hidex": 7,
            # "RapidPick": 8,
            # "TorreyPinesRIC20": 9,
        }

        # *Set Protocol Name
        try:
            if filename != None:
                self.setDisplayName(displayName)
            else:
                self.setDisplayName("NewProtocol")
        except Exception as error:
            print("Error setting protocol display name.")
            print(error)
        # *Open protocol file for editing
        try:
            if filename != None:
                self.setFile(filename)
        except Exception as error:
            print("Error creating SoftLinx protocol with filename %s: " % filename)
            print(error)
            return
        # *Initialize Protocol Steps
        try:
            if protocolSteps != None:
                self.setProtocolSteps(protocolSteps)
            else:
                self.setProtocolSteps([])
        except Exception as error:
            print("Error setting protocol steps.")
            print(error)
            return
        # *Initialize Variables
        try:
            if variables != None:
                self.setVariables(variables)
            else:
                self.setVariables([])
        except Exception as error:
            print("Error setting variables.")
            print(error)
            return
        # *Initialize Plates
        try:
            if plates != None:
                self.setPlates(plates)
            else:
                self.setPlates({})
        except Exception as error:
            print("Error setting plates.")
            print(error)
            return

    def setDisplayName(self, displayName):
        if not isinstance(displayName, str):
            raise TypeError("Display Name must be a string")
        self.displayName = displayName

    def setFile(self, filename):
        if not isinstance(filename, str):
            raise TypeError("filename must be a string.")
        self.filename = filename

    def setProtocolSteps(self, protocolSteps):
        if not isinstance(protocolSteps, list):
            raise TypeError("Protocol Steps must be a List.")
        self.protocolSteps = protocolSteps

    def setVariables(self, variables):
        if not isinstance(variables, list):
            raise TypeError("Variables must be a List.")
        self.variables = variables

    def setPlates(self, plates):
        if not isinstance(plates, dict):
            raise TypeError(
                "Plates must be a dict with key 'position' and value 'plate name'."
            )
        self.plates = plates

    # * SoftLinx Steps * #
    def conditional(
        self,
        conditionalStatement="",
        branchTrue=[],
        branchFalse=[],
        isActive=True,
        displayName="Conditional Statement",
        index=None,
        inplace=True,
    ):
        if not isinstance(branchTrue, list) or not isinstance(branchFalse, list):
            raise ValueError("branchTrue and branchFalse must be a list of steps")
        step = {
            "type": "IfElseActivity",
            "DisplayName": str(displayName),
            "Command": "IfElseActivity",
            "ToolTip": "If '%s'..." % (conditionalStatement),
            "SLXId": "7744fd63-8699-40b9-9241-741e701dd8b3",
            "isActive": str(isActive),
            "branchTrue": branchTrue,
            "branchFalse": branchFalse,
            "conditionalStatement": str(conditionalStatement),
        }

        if inplace:
            if index != None:
                self.protocolSteps.insert(index, step)
            else:
                self.protocolSteps.append(step)
        return step

    def parallel(
        self,
        branches=[[]],
        isActive=True,
        displayName="Parallel Activity",
        orderByVariable=False,
        orderVariable="",
        fixedOrder=[],
        index=None,
        inplace=True,
    ):
        if not isinstance(branches, list) or not all(
            [isinstance(branch, list) for branch in branches]
        ):
            raise ValueError("branches must be a list of lists.")
        step = {
            "type": "ParallelActivity",
            "DisplayName": str(displayName),
            "Command": "ParallelActivity",
            "ToolTip": "",
            "SLXId": "0ed9f8ba-5f2b-4f1c-a33a-edaec93b23c",
            "isActive": str(isActive),
            "branches": branches,
            "branchOrder": str(fixedOrder),
            "orderVariable": orderVariable,
        }
        if not orderByVariable and fixedOrder == []:
            step["IsStandard"] = "True"
        else:
            step["IsStandard"] = "False"
        if orderByVariable:
            step["IsByVariable"] = "True"
        else:
            step["IsByVariable"] = "False"
        if fixedOrder != []:
            step["IsOrdered"] = "True"
        else:
            step["IsOrdered"] = "False"
        if inplace:
            if index != None:
                self.protocolSteps.insert(index, step)
            else:
                self.protocolSteps.append(step)
        return step

    def runProgram(
        self,
        command="",
        variable_name="",
        hide_prompt=False,
        is_variable=False,
        is_constant=True,
        wait_for_complete=False,
        arguments="",
        isActive=True,
        index=None,
        inplace=True,
    ):
        if not isinstance(hide_prompt, bool):
            raise TypeError("hide_prompt should be a boolean.")
        if not isinstance(is_variable, bool):
            raise TypeError("is_variable should be a boolean.")
        if not isinstance(is_constant, bool):
            raise TypeError("is_constant should be a boolean.")
        if not isinstance(wait_for_complete, bool):
            raise TypeError("wait_for_complete should be a boolean.")
        step = {
            "type": "RunProgramActivity",
            "CommandLine": "",
            "Description": "Run: '%s'" % str(command),
            "Command": str(command),
            "VariableName": str(variable_name),
            "HidePrompt": bool(hide_prompt),
            "IsVariable": bool(is_variable),
            "IsConstant": bool(is_constant),
            "Arguments": str(arguments),
            "WaitForComplete": bool(wait_for_complete),
            "SLXId": "aa9c6603-467b-4c4f-81b3-49bb7dd0f768",
            "ToolTip": "Run: '%s'" % str(command),
            "isActive": str(isActive),
        }
        if inplace:
            if index != None:
                self.protocolSteps.insert(index, step)
            else:
                self.protocolSteps.append(step)
        return step

    # * Plate Crane Steps * #
    def plateCraneMoveCrane(
        self,
        position="SoftLinx.PlateCrane.Safe",
        isActive=True,
        index=None,
        inplace=True,
    ):
        step = {
            "type": "MoveCrane",
            "Command": "Move Crane",
            "Description": "MoveCrane to '%s'" % position,
            "SLXId": "83279d2c-43f7-4f36-8515-103a2f9a3de9",
            "ToolTip": "MoveCrane to '%s'" % position,
            "isActive": str(isActive),
            "system": "PlateCrane",
            "args": [["x:String", position]],
        }

        if inplace:
            if index != None:
                self.protocolSteps.insert(index, step)
            else:
                self.protocolSteps.append(step)
        return step

    def plateCraneMovePlate(
        self,
        positionsFrom=["SoftLinx.PlateCrane.Stack1"],
        positionsTo=["SoftLinx.PlateCrane.Stack2"],
        hasLid=False,
        inGripper=False,
        flip180=False,
        onEmptyStack="End Method",
        onMoveComplete="Move to Safe Location",
        moveUp=999,
        nestIsSpringLoaded=False,
        checkForPlatesInAllPositions=False,
        isActive=True,
        index=None,
        inplace=True,
    ):
        if inGripper:
            positionsFrom = ["SoftLinx.PlateCrane.Gripper"]
        if not isinstance(positionsFrom, list) or not isinstance(positionsTo, list):
            raise ValueError("positionsFrom and positionsTo must be Lists.")
        onEmptyStackDict = {
            "End Method": 0,
            "Post Message and Continue": 1,
            "Prompt User": 0,
            "Complete Method": 256,
            "Ignore and Continue": 512,
        }
        onMoveCompleteDict = {
            "Move Up": "Up",
            "Move to Safe Location": "Safe",
            "Hold Plate in Nest": "Hold",
            "Wait for Lid Removal": "Lid",
        }
        if isinstance(onEmptyStack, str):
            try:
                onEmptyStackVal = onEmptyStackDict[onEmptyStack]
            except:
                raise ValueError(
                    "onEmptyStack must be one of the following:"
                    + str([key + ", " for key in onEmptyStackDict])
                )
        else:
            raise ValueError(
                "onEmptyStack must be one of the following:"
                + str([key + ", " for key in onEmptyStackDict])
            )
        if checkForPlatesInAllPositions:
            onEmptyStackVal += 240
        if isinstance(onMoveComplete, str):
            try:
                onMoveCompleteVal = onMoveCompleteDict[onMoveComplete]
            except:
                raise ValueError(
                    "onMoveComplete must be one of the following:"
                    + str([key + ", " for key in onMoveCompleteDict])
                )
        else:
            raise ValueError(
                "onMoveComplete must be one of the following:"
                + str([key + ", " for key in onMoveCompleteDict])
            )
        if onMoveCompleteVal == "Up":
            if not isinstance(moveUp, int):
                raise ValueError("moveUp must be an integer")
            onMoveCompleteVal += str(moveUp)
        step = {
            "type": "MovePlate",
            "Command": "Move Plate",
            "Description": "From:      %s" % ",".join(positionsFrom)
            + "&#xD;&#xA;"
            + "To: %s" % ",".join(positionsTo),
            "SLXId": "9dabc6a5-8b05-434b-b7e8-b56f8d4cdb7d",
            "ToolTip": "From:      %s" % ",".join(positionsFrom)
            + "&#xD;&#xA;"
            + "To: %s" % ",".join(positionsTo),
            "isActive": str(isActive),
            "system": "PlateCrane",
            "args": [
                ["x:String", ",".join(positionsFrom)],
                ["x:String", ",".join(positionsTo)],
                ["x:String", str(onMoveCompleteVal)],
                ["x:String", str(onEmptyStackVal)],
                ["x:String", " "],
                ["x:String", str(hasLid)],
                ["x:String", str(nestIsSpringLoaded)],
                ["x:String", str(flip180)],
                ["x:String", " "],
            ],
        }

        if inplace:
            if index != None:
                self.protocolSteps.insert(index, step)
            else:
                self.protocolSteps.append(step)
        return step

    def plateCraneRemoveLid(
        self,
        positionsFrom=["SoftLinx.PlateCrane.Stack1"],
        positionsTo=["SoftLinx.PlateCrane.Stack2"],
        onEmptyStack="End Method",
        moveUpAndHoldLid=False,
        moveUpAmount=10,
        checkForPlatesInAllStacks=False,
        isActive=True,
        index=None,
        inplace=True,
    ):
        if not isinstance(positionsFrom, list) or not isinstance(positionsTo, list):
            raise ValueError("positionsFrom and positionsTo must be Lists.")
        onEmptyStackDict = {
            "End Method": 0,
            "Post Message and Continue": 1,
        }
        if isinstance(onEmptyStack, str):
            try:
                onEmptyStackVal = onEmptyStackDict[onEmptyStack]
            except:
                raise ValueError(
                    "onEmptyStack must be one of the following:"
                    + str([key + ", " for key in onEmptyStackDict])
                )
        else:
            raise ValueError(
                "onEmptyStack must be one of the following:"
                + str([key + ", " for key in onEmptyStackDict])
            )
        if checkForPlatesInAllStacks:
            onEmptyStackVal += 240
        if moveUpAndHoldLid:
            if not isinstance(moveUpAmount, int):
                raise ValueError("moveUp must be an integer")
        else:
            moveUpAmount = 0

        step = {
            "type": "RemoveLid",
            "Command": "Remove Lid",
            "Description": "RemoveLid from: %s" % ",".join(positionsFrom)
            + " to %s" % ",".join(positionsTo),
            "SLXId": "99bd7bce-806b-416b-9458-c39afda998d8",
            "ToolTip": "RemoveLid from: %s" % ",".join(positionsFrom)
            + " to %s" % ",".join(positionsTo),
            "isActive": str(isActive),
            "system": "PlateCrane",
            "args": [
                ["x:String", ",".join(positionsFrom)],
                ["x:String", ",".join(positionsTo)],
                ["x:String", str(moveUpAmount)],
                ["x:String", str(onEmptyStackVal)],
                ["x:String", " "],
            ],
        }

        if inplace:
            if index != None:
                self.protocolSteps.insert(index, step)
            else:
                self.protocolSteps.append(step)
        return step

    def plateCraneReplaceLid(
        self,
        positionsFrom=["SoftLinx.PlateCrane.Stack1"],
        positionsTo=["SoftLinx.PlateCrane.Stack2"],
        lidInGripper=False,
        isActive=True,
        index=None,
        inplace=True,
    ):
        if lidInGripper:
            positionsFrom = [" "]
        if not isinstance(positionsFrom, list) or not isinstance(positionsTo, list):
            raise ValueError("positionsFrom and positionsTo must be Lists.")

        step = {
            "type": "ReplaceLid",
            "Command": "Replace Lid",
            "Description": "ReplaceLid from: %s" % ",".join(positionsFrom)
            + " onto Plate in %s" % ",".join(positionsTo),
            "SLXId": "99bd7bce-806b-416b-9458-c39afda998d8",
            "ToolTip": "ReplaceLid from: %s" % ",".join(positionsFrom)
            + " onto Plate in %s" % ",".join(positionsTo),
            "isActive": str(isActive),
            "system": "PlateCrane",
            "args": [
                ["x:String", ",".join(positionsFrom)],
                ["x:String", ",".join(positionsTo)],
                ["x:String", "False"],
                ["x:String", " "],
            ],
        }

        if inplace:
            if index != None:
                self.protocolSteps.insert(index, step)
            else:
                self.protocolSteps.append(step)
        return step

    # * SoloSoft Steps * #
    def soloSoftRun(
        self, filename="protocol.hso", isActive=True, index=None, inplace=True
    ):
        step = {
            "type": "Run",
            "Command": "Run",
            "Description": "Protocol: " + filename,
            "SLXId": "5eb5e609-1660-4c5b-ade7-f51828196e13",
            "ToolTip": "Protocol: " + filename,
            "isActive": str(isActive),
            "system": "Solo",
            "args": [
                ["x:String", filename],
            ],
        }

        if inplace:
            if index != None:
                self.protocolSteps.insert(index, step)
            else:
                self.protocolSteps.append(step)
        # * Add .hso filename to manifest list
        if "\\" in filename:
            hso_filename = filename.split("\\")[-1]
        elif "/" in filename:
            hso_filename = filename.split("/")[-1]
        else:
            hso_filename = filename
        self.addToManifest(hso_filename)

        return step

    def soloSoftResetTipCount(
        self, position=1, isActive=True, index=None, inplace=True
    ):
        if not isinstance(position, int):
            raise TypeError("position must be an integer")
        if position < 1 or position > 8:
            raise ValueError("position must be between 1 and 8, inclusive")
        step = {
            "type": "Reset Tip Count",
            "Command": "Reset Tip Count",
            "Description": "Position:		" + str(position),
            "SLXId": "148788b4-63eb-4424-9af8-a175fb195afb",
            "ToolTip": "Position:		" + str(position),
            "isActive": str(isActive),
            "system": "Solo",
            "args": [
                ["x:String", str(position)],
            ],
        }
        if inplace:
            if index != None:
                self.protocolSteps.insert(index, step)
            else:
                self.protocolSteps.append(step)

    # * Hidex Steps * #
    def hidexRun(self, hidex_protocol, isActive=True, index=None, inplace=True):
        if not isinstance(hidex_protocol, str):
            raise TypeError(
                "hidex_protocol must be a string corresponding to the name of an assay protocol"
            )
        step = {
            "type": "Run",
            "Command": "Run",
            "Description": "Assay: " + hidex_protocol,
            "SLXId": "8e5c1758-fa8b-43e2-87dc-c90431662395",
            "ToolTip": "Assay: " + hidex_protocol,
            "isActive": str(isActive),
            "system": "Hidex",
            "args": [
                ["x:String", hidex_protocol],
            ],
        }
        if inplace:
            if index != None:
                self.protocolSteps.insert(index, step)
            else:
                self.protocolSteps.append(step)

    def hidexOpen(self, isActive=True, index=None, inplace=True):
        step = {
            "type": "Open Door",
            "Command": "Open Door",
            "Description": "",
            "SLXId": "62c47122-48c6-413a-a41b-9ff35a0489fc",
            "ToolTip": "",
            "isActive": str(isActive),
            "system": "Hidex",
            "args": [],
        }
        if inplace:
            if index != None:
                self.protocolSteps.insert(index, step)
            else:
                self.protocolSteps.append(step)

    def hidexClose(self, isActive=True, index=None, inplace=True):
        step = {
            "type": "Close Door",
            "Command": "Close Door",
            "Description": "",
            "SLXId": "9d060013-be01-403d-b15a-b0ce9da34cb3",
            "ToolTip": "",
            "isActive": str(isActive),
            "system": "Hidex",
            "args": [],
        }
        if inplace:
            if index != None:
                self.protocolSteps.insert(index, step)
            else:
                self.protocolSteps.append(step)

    # * Output * #
    def saveProtocol(self, filename=None, generate_ahk=True):
        if filename == None:
            if self.filename != None:
                filename = self.filename
            else:
                raise BaseException("Need to specify a filename to save a protocol.")

        if len(self.plates) > 0:
            self.plugin_flags["Plates"] = True

        # *Start Constructing XML
        protocol_dict = {
            "mc:Ignorable": "sap sap2010 sads",
            "PreProtocolWizard": "{x:Null}",
            "ActivityLabel": "",
            "DisplayName": self.displayName,
            "HasConstraints": "False",
            "sap2010:WorkflowViewState.IdRef": "Protocol_1",
            "SLXId": "df50c4dd-572a-41df-a285-0caf0907a053",
            "ToolTip": "",
            "UserComments": "",
            "isActive": "True",
            "isSetup": "True",
            "xmlns": "clr-namespace:Hudson.Workflow.Activities;assembly=Hudson.Workflow.Activities",
            "xmlns:hcc": "clr-namespace:Hudson.Common.Communications;assembly=Hudson.Common",
            "xmlns:hwab": "clr-namespace:Hudson.Workflow.Activities.Base;assembly=SoftLinxBaseActivities",
            "xmlns:mc": "http://schemas.openxmlformats.org/markup-compatibility/2006",
            "xmlns:p": "http://schemas.microsoft.com/netfx/2009/xaml/activities",
            "xmlns:s": "clr-namespace:System;assembly=mscorlib",
            "xmlns:sads": "http://schemas.microsoft.com/netfx/2010/xaml/activities/debugger",
            "xmlns:sap": "http://schemas.microsoft.com/netfx/2009/xaml/activities/presentation",
            "xmlns:sap2010": "http://schemas.microsoft.com/netfx/2010/xaml/activities/presentation",
            "xmlns:scg": "clr-namespace:System.Collections.Generic;assembly=mscorlib",
            "xmlns:x": "http://schemas.microsoft.com/winfx/2006/xaml",
        }
        protocol = ET.Element(
            "Protocol",
            protocol_dict,
        )

        # *Activities
        activities = ET.SubElement(protocol, "Protocol.Activities")
        scg_list = ET.SubElement(
            activities,
            "scg:List",
            {
                "x:TypeArguments": "p:Activity",
                "Capacity": "4",
            },
        )
        # *Add each step in the protocol
        for step in self.protocolSteps:
            self.generateStepXML(scg_list, step)
        activities2 = ET.SubElement(protocol, "Protocol.Activities2")
        scg_list = ET.SubElement(
            activities2,
            "scg:List",
            {"x:TypeArguments": "p:Activity", "Capacity": "0"},
        )
        initialValues = ET.SubElement(protocol, "Protocol.InitialValues")
        scg_dict = ET.SubElement(
            initialValues,
            "scg:Dictionary",
            {"x:TypeArguments": "x:String, hwab:Variable"},
        )

        # *Add each plugin
        interfaces = ET.SubElement(protocol, "Protocol.Interfaces")
        scg_dict = ET.SubElement(
            interfaces,
            "scg:Dictionary",
            {"x:TypeArguments": "hcc:SLAddress, hwab:Interface"},
        )
        self.generatePluginInterface(scg_dict, "PlateCrane")
        self.generatePluginInterface(scg_dict, "Plates")
        self.generatePluginInterface(scg_dict, "Solo")
        self.generatePluginInterface(scg_dict, "Hidex")
        # self.generatePluginInterface(interfaces, "PlateCrane")
        # self.generatePluginInterface(interfaces, "Plates")
        # self.generatePluginInterface(interfaces, "RapidPick")
        # self.generatePluginInterface(interfaces, "Solo")
        # self.generatePluginInterface(interfaces, "TorreyPinesRIC20")

        # *TimeConstraints
        timeConstraints = ET.SubElement(protocol, "Protocol.TimeConstraints")
        scg_list = ET.SubElement(
            timeConstraints,
            "scg:List",
            {"x:TypeArguments": "hwab:TimeConstraint", "Capacity": "0"},
        )

        # *Variables
        variables = ET.SubElement(protocol, "Protocol.Variables")
        variableList = ET.SubElement(
            variables, "hwab:VariableList", {"SLXHost": "{x:Null}"}
        )
        self.generatePluginVariables(variableList, "PlateCrane")
        self.generatePluginVariables(variableList, "Plates")
        # self.generatePluginVariables(variableList, "RapidPick")
        self.generatePluginVariables(variableList, "Hidex")
        self.generatePluginVariables(variableList, "Solo")
        # self.generatePluginVariables(variableList, "TorreyPinesRIC20")

        # *Add each variable
        # for variable in self.variables:
        #     variable_xml = ET.SubElement(variableList, variable.xml())

        workflowViewState = ET.SubElement(
            protocol, "sap2010:WorkflowViewState.ViewStateManager"
        )
        viewStateManager = ET.SubElement(workflowViewState, "sap2010:ViewStateManager")
        viewStateData = ET.SubElement(
            viewStateManager,
            "sap2010:ViewStateData",
            {
                "Id": "Protocol_1",
                "sap:VirtualizedContainerService.HintSize": "205,119",
            },
        )
        debugSymbol = ET.SubElement(protocol, "sads:DebugSymbol.Symbol")
        debugSymbol.text = (
            "dypDOlxVc2Vyc1xyeWFuZFxEZXZcTmV3UHJvdG9jb2xfcGx1Z2luLnNsdnABAQFqDAEB"
        )
        tree = ET.ElementTree(self.indent(protocol))
        xmlstring = ET.tostring(
            tree.getroot(), method="xml", encoding="unicode"
        ).replace("&amp;", "&")
        with open(filename, "w") as file:
            file.write(xmlstring)
        # *Add .slvp filename to manifest list
        self.addToManifest(os.path.basename(filename))
        # *Generate AutoHotKey script
        self.generateAutoHotKey(
            os.path.basename(filename), os.path.splitext(filename)[0] + ".ahk"
        )
        # *Add AutoHotKey filename to manifest list
        self.addToManifest(os.path.splitext(os.path.basename(filename))[0] + ".ahk")
        # *Generate Manifest File
        self.generateManifest()

    # * Manifest Handler *#
    def addToManifest(self, filename):
        if not isinstance(filename, str):
            raise TypeError("filename must be a string to add to manifest.")
        self.manifest_list.append(filename)

    # *Pretty-print XML
    def indent(self, element, level=0):
        i = "\n" + level * "  "
        j = "\n" + (level - 1) * "  "
        if len(element):
            if not element.text or not element.text.strip():
                element.text = i + "  "
            if not element.tail or not element.tail.strip():
                element.tail = i
            for subelem in element:
                self.indent(subelem, level + 1)
            if not element.tail or not element.tail.strip():
                element.tail = j
        else:
            if level and (not element.tail or not element.tail.strip()):
                element.tail = j
        return element

    # * Output File Generators * #
    def generateManifest(self, manifest_filename=None):
        if manifest_filename == None:
            manifest_filename = os.path.splitext(self.filename)[0] + ".txt"
        else:
            manifest_filename = os.path.abspath(self.filename).replace(
                os.path.basename(self.filename), manifest_filename
            )

        with open(manifest_filename, "w+") as manifest_file:
            manifest_file.write(
                str(time.time()) + "\n" + str(datetime.datetime.now()) + "\n"
            )  # add timestamps
            manifest_file.writelines("\n".join(self.manifest_list))

    def generateAutoHotKey(self, softlinx_filename=None, ahk_filename=None):
        if ahk_filename == None:
            ahk_filename = os.path.splitext(self.filename)[0] + ".ahk"
        if softlinx_filename == None:
            softlinx_filename = self.filename
        if softlinx_filename == None:
            raise Exception(
                "Cannot generate AutoHotKey script without a softlinx filename."
            )
        with open(ahk_filename, "w") as file:
            file.write(
                """
#SingleInstance, Force
#WinActivateForce
SendMode Input
SetWorkingDir, %%A_ScriptDir%%
SetTitleMatchMode, 2

if WinExist("User Cancelled Run")
{
    WinActivate
    Send, {Enter}
    Sleep, 500
}
if WinExist("ahk_exe SoftLinxVProtocolEditor.exe")
{
    WinClose
    Sleep, 1000
    if WinExist("ahk_exe SoftLinxVProtocolEditor.exe")
    {
        MsgBox, Couldn't close SoftLinx V, please close it manually and restart this run.
        return
    }
}
if WinExist("ahk_exe SOLOSoft.exe")
{
    MsgBox, SOLOSoft is still running. Please kill it, then press "OK" below to resume execution.
    if WinExist("ahk_exe SOLOSoft.exe")
    {
        MsgBox, SOLOSoft is still running, please close it manually and restart this run.
        return
    }
}
Sleep, 1000
Run, "C:\Program Files (x86)\Hudson Robotics\SoftLinx V\SoftLinxVProtocolEditor.exe" %%A_ScriptDir%%\\%s
WinWaitActive, SoftLinx V,,10
if ErrorLevel
{
    WinGetActiveTitle, Title
    MsgBox, Couldn't find SoftLinx V window. The active window is "%%Title%%".
    return
}
Sleep, 5000
MouseClick, Left, 300, 45
Sleep, 1000
if WinActive("Not Saved") {
    Send, {Tab}{Enter}
    Sleep, 5000
}
if WinActive("Start Now?") {
    Send, {Enter}
    Sleep, 5000
}
else
{
    MsgBox, Error starting run.
    return
}
                """
                % softlinx_filename
            )

    def generatePluginVariables(self, parentXML, system):
        variable = ET.SubElement(
            parentXML,
            "hwab:Variable",
            {
                "x:TypeArguments": "hwab:Interface",
                "Value": "{x:Reference __ReferenceID%d}"
                % self.plugin_reference[system],
                "x:Key": "SoftLinx." + system,
                "Name": "SoftLinx." + system,
                "Prompt": "False",
            },
        )
        default = ET.SubElement(variable, "hwab:Variable.Default")
        if system == "Plates" and len(self.plates):
            interface = ET.SubElement(
                default,
                "hwab:Interface",
                {
                    "x:Name": "__ReferenceID" + str(self.plugin_reference[system]),
                    "AddinType": system,
                },
            )
            interface_address = ET.SubElement(interface, "hwab:Interface.Address")
            setupData = ET.SubElement(interface, "hwab:Interface.SetupData")
            array = ET.SubElement(setupData, "x:Array", {"Type": "x:String"})
            for key, value in self.plates.items():
                element = ET.SubElement(array, "x:String")
                element.text = key + "=" + value
        else:
            interface = ET.SubElement(
                default,
                "hwab:Interface",
                {
                    "SetupData": "{x:Null}",
                    "x:Name": "__ReferenceID" + str(self.plugin_reference[system]),
                    "AddinType": system,
                },
            )
            interface_address = ET.SubElement(interface, "hwab:Interface.Address")
        sladdress = ET.SubElement(
            interface_address,
            "hcc:SLAddress",
            {
                "x:Name": "__ReferenceID%d" % self.plugin_address[system],
                "Name": system,
                "Workcell": "SoftLinx",
            },
        )

    # * XML Generators * #
    def generatePluginInterface(self, parentXML, system):
        ref = ET.SubElement(parentXML, "x:Reference")
        ref.text = "__ReferenceID%d" % self.plugin_reference[system]
        key = ET.SubElement(ref, "x:Key")
        sub_ref = ET.SubElement(key, "x:Reference")
        sub_ref.text = "__ReferenceID%d" % self.plugin_address[system]

    def generateConditionalXML(self, parent, step):
        activity_dict = {
            "Text": "{x:Null}",
            "ActivityLabel": "",
            "DisplayName": step["DisplayName"],
            "HasConstraints": "False",
            "SLXId": step["SLXId"],
            "ToolTip": step["ToolTip"],
            "UserComments": "",
            "isActive": step["isActive"],
            "isSetup": "True",
        }
        ifelse_xml = ET.SubElement(parent, "IfElseActivity", activity_dict)
        ifelse_activities = ET.SubElement(ifelse_xml, "IfElseActivity.Activities")
        scg_list = ET.SubElement(
            ifelse_activities,
            "scg:List",
            {
                "x:TypeArguments": "p:Activity",
                "Capacity": "4",
            },
        )
        for substep in step["branchTrue"]:
            self.generateStepXML(scg_list, substep)
        ifelse_activities2 = ET.SubElement(ifelse_xml, "IfElseActivity.Activities2")
        scg_list = ET.SubElement(
            ifelse_activities2,
            "scg:List",
            {
                "x:TypeArguments": "p:Activity",
                "Capacity": "4",
            },
        )
        for substep in step["branchFalse"]:
            self.generateStepXML(scg_list, substep)
        ifelse_arguments = ET.SubElement(ifelse_xml, "IfElseActivity.Arguments")
        ET.SubElement(
            ifelse_arguments,
            "IfElseActivityArguments",
            {"Condition": step["conditionalStatement"]},
        )
        ifelse_timeconstraints = ET.SubElement(
            ifelse_xml, "IfElseActivity.TimeConstraints"
        )
        ET.SubElement(
            ifelse_timeconstraints,
            "scg:List",
            {
                "x:TypeArguments": "hwab:TimeConstraint",
                "Capacity": "0",
            },
        )

    def generateParallelXML(self, parent, step):
        activity_dict = {
            "Text": "{x:Null}",
            "ActivityLabel": "",
            "DisplayName": step["DisplayName"],
            "HasConstraints": "False",
            "SLXId": step["SLXId"],
            "ToolTip": step["ToolTip"],
            "UserComments": "",
            "isActive": step["isActive"],
            "isSetup": "True",
        }
        parallel_xml = ET.SubElement(parent, "ParallelActivity", activity_dict)
        parallelactivity_activities = ET.SubElement(
            parallel_xml, "ParallelActivity.Activities"
        )
        scg_list = ET.SubElement(
            parallelactivity_activities,
            "scg:List",
            {
                "x:TypeArguments": "p:Activity",
                "Capacity": "4",
            },
        )
        branch_count = 0
        for branch in step["branches"]:
            branch_count += 1
            branch_activity = ET.SubElement(
                scg_list,
                "BranchActivity",
                {
                    "ActivityLabel": "",
                    "DisplayName": "Branch " + str(branch_count),
                    "HasConstraints": "False",
                    "SLXId": "38784045-5053-4b14-bbc1-cf98a8b35a23",
                    "ToolTip": "",
                    "UserComments": "",
                    "isActive": "True",
                    "isSetup": "True",
                },
            )
            branch_activity_activities = ET.SubElement(
                branch_activity, "BranchActivity.Activities"
            )
            branch_scg_list = ET.SubElement(
                branch_activity_activities,
                "scg:List",
                {
                    "x:TypeArguments": "p:Activity",
                    "Capacity": "4",
                },
            )
            for substep in branch:
                self.generateStepXML(branch_scg_list, substep)
            branch_activity_activities2 = ET.SubElement(
                branch_activity, "BranchActivity.Activities2"
            )
            branch_scg_list2 = ET.SubElement(
                branch_activity_activities2,
                "scg:List",
                {
                    "x:TypeArguments": "p:Activity",
                    "Capacity": "0",
                },
            )
            branch_time_constraints = ET.SubElement(
                branch_activity, "BranchActivity.TimeConstraints"
            )
            time_scg_list = ET.SubElement(
                branch_time_constraints,
                "scg:List",
                {
                    "x:TypeArguments": "hwab:TimeConstraint",
                    "Capacity": "0",
                },
            )

        parallel_activities2 = ET.SubElement(
            parallel_xml, "ParallelActivity.Activities2"
        )
        scg_list = ET.SubElement(
            parallel_activities2,
            "scg:List",
            {
                "x:TypeArguments": "p:Activity",
                "Capacity": "0",
            },
        )
        parallel_arguments = ET.SubElement(parallel_xml, "ParallelActivity.Arguments")
        ET.SubElement(
            parallel_arguments,
            "ParallelActivityArguments",
            {
                "BranchOrder": step["branchOrder"],
                "IsByVariable": step["IsByVariable"],
                "IsOrdered": step["IsOrdered"],
                "IsStandard": step["IsStandard"],
                "VariableName": step["orderVariable"],
            },
        )
        parallel_timeconstraints = ET.SubElement(
            parallel_xml, "ParallelActivity.TimeConstraints"
        )
        ET.SubElement(
            parallel_timeconstraints,
            "scg:List",
            {
                "x:TypeArguments": "hwab:TimeConstraint",
                "Capacity": "0",
            },
        )

    def generateRunProgramXML(self, parent, step):
        activity_dict = {
            "CommandLine": step["CommandLine"],
            "Description": step["Description"],
            "DisplayName": "Run Program",
            "HasConstraints": "False",
            "SLXId": step["SLXId"],
            "ToolTip": step["ToolTip"],
            "UserComments": "",
            "isActive": step["isActive"],
            "isCanceled": "False",
            "isSetup": "True",
        }
        run_xml = ET.SubElement(parent, "RunProgramActivity", activity_dict)
        run_arguments = ET.SubElement(run_xml, "RunProgramActivity.Arguments")
        ET.SubElement(
            run_arguments,
            "RunProgramActivityArguments",
            {
                "Command": str(step["Command"]),
                "VariableName": str(step["VariableName"]),
                "HidePrompt": str(step["HidePrompt"]),
                "IsVariable": str(step["IsVariable"]),
                "IsConstant": str(step["IsConstant"]),
                "Arguments": str(step["Arguments"]),
                "WaitForComplete": str(step["WaitForComplete"]),
            },
        )
        run_timeconstraints = ET.SubElement(
            run_xml, "RunProgramActivity.TimeConstraints"
        )
        ET.SubElement(
            run_timeconstraints,
            "scg:List",
            {
                "x:TypeArguments": "hwab:TimeConstraint",
                "Capacity": "0",
            },
        )

    def generateStepXML(self, scg_list, step):
        if step["type"] == "IfElseActivity":
            self.generateConditionalXML(scg_list, step)
            return
        if step["type"] == "IfElseActivity":
            self.generateParallelXML(scg_list, step)
            return
        if step["type"] == "RunProgramActivity":
            self.generateRunProgramXML(scg_list, step)
            return
        self.plugin_flags[step["system"]] = True
        activity_dict = {
            "IconPath": "{x:Null}",
            "CommandLine": step["Command"],
            "Description": step["Description"],
            "DisplayName": step["system"],
            "HasConstraints": "False",
            "SLXId": step["SLXId"],
            "ToolTip": step["ToolTip"],
            "UserComments": "",
            "isActive": step["isActive"],
            "isCanceled": "False",
            "isSetup": "True",
        }
        step_xml = ET.SubElement(scg_list, "InstrumentActivity", activity_dict)
        arguments = ET.SubElement(step_xml, "InstrumentActivity.Arguments")
        instrument_arguments = ET.SubElement(
            arguments,
            "InstrumentActivityArguments",
            {
                "Address": "{x:Reference __ReferenceID%d}"
                % self.plugin_address[step["system"]],
                "ResultVariable": "{x:Null}",
                "AddinType": step["system"],
                "Command": step["Command"],
            },
        )
        iarg_arg = ET.SubElement(
            instrument_arguments, "InstrumentActivityArguments.Arguments"
        )
        arg_list = ET.SubElement(
            iarg_arg,
            "scg:List",
            {"x:TypeArguments": "x:Object", "Capacity": str(len(step["args"]))},
        )
        for arg in step["args"]:
            arg_xml = ET.SubElement(arg_list, arg[0])
            arg_xml.text = arg[1]
        iarg_hWnd = ET.SubElement(
            instrument_arguments, "InstrumentActivityArguments.hWnd"
        )
        s = ET.SubElement(iarg_hWnd, "s:IntPtr")

        time_constraints = ET.SubElement(step_xml, "InstrumentActivity.TimeConstraints")
        constraint_list = ET.SubElement(
            time_constraints,
            "scg:List",
            {
                "x:TypeArguments": "hwab:TimeConstraint",
                "Capacity": "0",
            },
        )
        workflowViewState = ET.SubElement(step_xml, "sap2010:WorkflowViewState.IdRef")
        workflowViewState.text = "InstrumentActivity_1"

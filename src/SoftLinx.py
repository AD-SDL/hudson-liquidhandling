import os
import xml.etree.ElementTree as ET


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
        self.plugin_flags = {
            "PlateCrane": False,
            "Plates": False,
            "Solo": False,
            "RapidPick": False,
            "TorreyPinesRIC20": False,
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

    def activityCapacityCalculator(self):
        if len(self.protocolSteps) > 0:
            return "4"
        else:
            return "0"

    def generatePluginVariables(self, variableList, reference, reference_address, name):
        variable = ET.SubElement(
            variableList,
            "hwab:Variable",
            {
                "x:TypeArguments": "hwab:Interface",
                "Value": "{x:Reference __ReferenceID%d}" % reference,
                "x:Key": "SoftLinx." + name,
                "Name": "SoftLinx." + name,
                "Prompt": "False",
            },
        )
        default = ET.SubElement(variable, "hwab:Variable.Default")
        interface = ET.SubElement(
            default,
            "hwab:Interface",
            {
                "SetupData": "{x:Null}",
                "x:Name": "__ReferenceID" + str(reference),
                "AddinType": name,
            },
        )
        interface_address = ET.SubElement(interface, "hwab:Interface.Address")
        sladdress = ET.SubElement(
            interface_address,
            "hcc:SLAddress",
            {
                # "x:Name": "__ReferenceID" + str(reference_address),
                "Name": name,
                "Workcell": "SoftLinx",
            },
        )

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
            file.write("#SingleInstance, Force\n")
            file.write("SendMode Input\n")
            file.write("SetWorkingDir, \%A_ScriptDir%\n")
            file.write("\n")
            file.write(
                'Run, "C:\Program Files (x86)\Hudson Robotics\SoftLinx V\SoftLinxVProtocolEditor.exe" '
                + softlinx_filename
                + "\n"
            )
            file.write("WinActivate, SoftLinx V\n")
            file.write("Sleep, 5000\n")
            file.write("#IfWinActive, Microsoft Visual Basic\n")
            file.write("MsgBox, Problem Running Pipeline - Check plugins\n")
            file.write("Exit")
            file.write("#If")
            file.write("\tMouseClick, Left, 300, 45\n")
            file.write("\tSleep, 1000\n")
            file.write("\t#IfWinActive, Not Saved\n")
            file.write("\tSend, {Tab}{Enter}\n")
            file.write("\tSleep, 1000\n")
            file.write("\t#IfWinActive, Start Now?\n")
            file.write("\tSend, {Enter}\n")
            file.write("\tSleep, 1000\n")

    def generateStepXML(self, scg_list, step):
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
                # "Address": "{x:Reference __ReferenceID%d}" % step["address"],
                "ResultVariable": "{x:Null}",
                "AddinType": step["system"],
                "Command": step["Command"],
            },
        )
        iarg_add = ET.SubElement(
            instrument_arguments, "InstrumentActivityArguments.Address"
        )
        sladdress = ET.SubElement(
            iarg_add,
            "hcc:SLAddress",
            {
                "x:Name": "__ReferenceID" + str(step["address"]),
                "Name": step["system"],
                "Workcell": "SoftLinx",
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
            "address": 5,
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
        isActive=True,
        index=None,
        inplace=True,
    ):
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
            "address": 5,
            "system": "PlateCrane",
            "args": [
                ["x:String", ",".join(positionsFrom)],
                ["x:String", ",".join(positionsTo)],
                ["x:String", "Safe"],
                ["x:String", "0"],
                ["x:String", " "],
                ["x:String", "False"],
                ["x:String", "False"],
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
            "address": 8,
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
        return step

    def saveProtocol(self, filename=None, generate_ahk=True):
        if filename == None:
            if self.filename != None:
                filename = self.filename
            else:
                raise BaseException("Need to specify a filename to save a protocol.")
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
        # *PlateCrane
        if self.plugin_flags["PlateCrane"]:
            plugin = ET.SubElement(
                interfaces,
                "hwab:Interface",
                {
                    "x:Key": "{x:Reference __ReferenceID5}",
                    "SetupData": "{x:Null}",
                    "Address": "{x:Reference __ReferenceID5}",
                    "AddinType": "PlateCrane",
                },
            )
        else:
            plugin = ET.SubElement(
                interfaces,
                "hwab:Interface",
                {
                    "x:Key": "{x:Reference __ReferenceID5}",
                    "SetupData": "{x:Null}",
                    "AddinType": "PlateCrane",
                },
            )
            address = ET.SubElement(plugin, "hwab:Interface.Address")
            sladdress = ET.SubElement(
                address,
                "hcc:SLAddress",
                {
                    "x:Name": "__ReferenceID5",
                    "Name": "PlateCrane",
                    "Workcell": "SoftLinx",
                },
            )
        # *Plate
        if len(self.plates) > 0:
            plugin = ET.SubElement(
                interfaces,
                "hwab:Interface",
                {
                    "x:Key": "{x:Reference __ReferenceID6}",
                    "AddinType": "Plates",
                },
            )
            address = ET.SubElement(plugin, "hwab:Interface.Address")
            sladdress = ET.SubElement(
                address,
                "hcc:SLAddress",
                {"x:Name": "__ReferenceID6", "Name": "Plates", "Workcell": "SoftLinx"},
            )
            setupData = ET.SubElement(plugin, "hwab:Interface.SetupData")
            array = ET.SubElement(setupData, "x:Array", {"Type": "x:String"})
            for key, value in self.plates.items():
                element = ET.SubElement(array, "x:String")
                element.text = key + "=" + value
        else:
            plugin = ET.SubElement(
                interfaces,
                "hwab:Interface",
                {
                    "x:Key": "{x:Reference __ReferenceID6}",
                    "SetupData": "{x:Null}",
                    "AddinType": "Plates",
                },
            )
            address = ET.SubElement(plugin, "hwab:Interface.Address")
            sladdress = ET.SubElement(
                address,
                "hcc:SLAddress",
                {"x:Name": "__ReferenceID6", "Name": "Plates", "Workcell": "SoftLinx"},
            )

        # *RapidPickSP
        if self.plugin_flags["TorreyPinesRIC20"]:
            plugin = ET.SubElement(
                interfaces,
                "hwab:Interface",
                {
                    "x:Key": "{x:Reference __ReferenceID7}",
                    "SetupData": "{x:Null}",
                    "Address": "{x:Reference __ReferenceID7}",
                    "AddinType": "RapidPick",
                },
            )
        else:
            plugin = ET.SubElement(
                interfaces,
                "hwab:Interface",
                {
                    "x:Key": "{x:Reference __ReferenceID7}",
                    "SetupData": "{x:Null}",
                    "AddinType": "RapidPick",
                },
            )
            address = ET.SubElement(plugin, "hwab:Interface.Address")
            sladdress = ET.SubElement(
                address,
                "hcc:SLAddress",
                {
                    "x:Name": "__ReferenceID7",
                    "Name": "RapidPick",
                    "Workcell": "SoftLinx",
                },
            )
        # *Solo
        if self.plugin_flags["Solo"]:
            plugin = ET.SubElement(
                interfaces,
                "hwab:Interface",
                {
                    "x:Key": "{x:Reference __ReferenceID8}",
                    "SetupData": "{x:Null}",
                    "Address": "{x:Reference __ReferenceID8}",
                    "AddinType": "Solo",
                },
            )
        else:
            plugin = ET.SubElement(
                interfaces,
                "hwab:Interface",
                {
                    "x:Key": "{x:Reference __ReferenceID8}",
                    "SetupData": "{x:Null}",
                    "AddinType": "Solo",
                },
            )
            address = ET.SubElement(plugin, "hwab:Interface.Address")
            sladdress = ET.SubElement(
                address,
                "hcc:SLAddress",
                {"x:Name": "__ReferenceID8", "Name": "Solo", "Workcell": "SoftLinx"},
            )
        # *TorreyPinesRIC20
        if self.plugin_flags["TorreyPinesRIC20"]:
            plugin = ET.SubElement(
                interfaces,
                "hwab:Interface",
                {
                    "x:Key": "{x:Reference __ReferenceID9}",
                    "SetupData": "{x:Null}",
                    "Address": "{x:Reference __ReferenceID9}",
                    "AddinType": "TorreyPinesRIC20",
                },
            )
        else:
            plugin = ET.SubElement(
                interfaces,
                "hwab:Interface",
                {
                    "x:Key": "{x:Reference __ReferenceID9}",
                    "SetupData": "{x:Null}",
                    "AddinType": "TorreyPinesRIC20",
                },
            )
            address = ET.SubElement(plugin, "hwab:Interface.Address")
            sladdress = ET.SubElement(
                address,
                "hcc:SLAddress",
                {
                    "x:Name": "__ReferenceID9",
                    "Name": "TorreyPinesRIC20",
                    "Workcell": "SoftLinx",
                },
            )

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
        self.generatePluginVariables(variableList, 0, 5, "PlateCrane")
        self.generatePluginVariables(variableList, 1, 6, "Plates")
        self.generatePluginVariables(variableList, 2, 7, "RapidPick")
        self.generatePluginVariables(variableList, 3, 8, "Solo")
        self.generatePluginVariables(variableList, 4, 9, "TorreyPinesRIC20")

        # *Add each variable
        for variable in self.variables:
            variable_xml = ET.SubElement(variableList, variable.xml())

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
        # !debugSymbol is probably some sort of hashed nonsense, which could be an issue
        # !Update: seems to be constructive rather than hashed. But it also doesn't seem to impact operation atm
        debugSymbol = ET.SubElement(protocol, "sads:DebugSymbol.Symbol")
        debugSymbol.text = (
            "dypDOlxVc2Vyc1xyeWFuZFxEZXZcTmV3UHJvdG9jb2xfcGx1Z2luLnNsdnABAQFqDAEB"
        )
        tree = ET.ElementTree(self.indent(protocol))
        # tree.write(filename, xml_declaration=False, encoding="utf-8")
        xmlstring = ET.tostring(
            tree.getroot(), method="xml", encoding="unicode"
        ).replace("&amp;", "&")
        with open(filename, "w") as file:
            file.write(xmlstring)
        # *Generate AutoHotKey script
        self.generateAutoHotKey(filename, os.path.splitext(filename)[0] + ".ahk")

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

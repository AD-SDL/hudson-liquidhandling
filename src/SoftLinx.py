import json
import Properties
import xml.etree.ElementTree as ET

from SoloSoft import STEP_DELIMITER


class SoftLinx:
    def __init__(
        self,
        displayName=None,
        filename=None,
        protocolSteps=None,
        variables=None,
    ):
        self.displayName = None
        self.filename = None
        self.protocolSteps = []
        self.variables = []

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

    def activityCapacityCalculator(self):
        if len(self.protocolSteps) > 0:
            return "4"
        else:
            return "0"

    def pluginVariable(self, variableList, reference, reference_address, name):
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
                "x:Name": "__ReferenceID" + str(reference_address),
                "Name": name,
                "Workcell": "SoftLinx",
            },
        )

    def generate_step_xml(self, scg_list, step):
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
                "Address": "{x:Reference __ReferenceID%d}" % step["address"],
                "ResultVariable": "{x:Null}",
                "AddinType": step["system"],
                "Command": step["Command"],
            },
        )
        iarg_arg = ET.SubElement(
            instrument_arguments, "InstrumentActivityArguments.Arguments"
        )
        arg_list = ET.SubElement(
            iarg_arg, "scg:List", {"x:TypeArguments": "x:Object", "Capacity": str(len(step["args"]))}
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

    def moveCrane(
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

    def movePlate(
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
            "Description": "", #"From:      %s&#xD;&#xA;To: %s" % (positionsFrom, positionsTo),
            "SLXId": "9dabc6a5-8b05-434b-b7e8-b56f8d4cdb7d",
            "ToolTip": "", #"From:      %s&#xD;&#xA;To: %s" % (positionsFrom, positionsTo),
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
            ]
        }

        if inplace:
            if index != None:
                self.protocolSteps.insert(index, step)
            else:
                self.protocolSteps.append(step)
        return step

    def saveProtocol(self, filename=None):
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
            "sap2010:WorkflowViewState.IdRef": "Protocol_1",
        }
        protocol = ET.Element(
            "Protocol",
            protocol_dict,
        )

        # *Activities
        activities = ET.SubElement(protocol, "Protocol.Activities")
        # !Capacity changes based on some factor...unclear exactly what though.
        scg_list = ET.SubElement(
            activities,
            "scg:List",
            {
                "x:TypeArguments": "p:Activity",
                "Capacity": self.activityCapacityCalculator(),
            },
        )
        # *Add each step in the protocol
        for step in self.protocolSteps:
            self.generate_step_xml(scg_list, step)
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
        plugin = ET.SubElement(
            interfaces,
            "hwab:Interface",
            {
                "x:Key": "{x:Reference __ReferenceID5}",
                "Address": "{x:Reference __ReferenceID5}",
                "SetupData": "{x:Null}",
                "AddinType": "PlateCrane",
            },
        )
        # *Plate
        plugin = ET.SubElement(
            interfaces,
            "hwab:Interface",
            {
                "x:Key": "{x:Reference __ReferenceID6}",
                "Address": "{x:Reference __ReferenceID6}",
                "SetupData": "{x:Null}",
                "AddinType": "Plates",
            },
        )
        # *RapidPickSP
        plugin = ET.SubElement(interfaces, "x:Reference")
        plugin.text = "__ReferenceID2"
        key = ET.SubElement(plugin, "x:Key")
        reference = ET.SubElement(key, "x:Reference")
        reference.text = "__ReferenceID7"
        # *Solo
        plugin = ET.SubElement(interfaces, "x:Reference")
        plugin.text = "__ReferenceID3"
        key = ET.SubElement(plugin, "x:Key")
        reference = ET.SubElement(key, "x:Reference")
        reference.text = "__ReferenceID8"
        # *TorreyPinesRIC20
        plugin = ET.SubElement(interfaces, "x:Reference")
        plugin.text = "__ReferenceID4"
        key = ET.SubElement(plugin, "x:Key")
        reference = ET.SubElement(key, "x:Reference")
        reference.text = "__ReferenceID9"

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
        self.pluginVariable(variableList, 0, 5, "PlateCrane")
        self.pluginVariable(variableList, 1, 6, "Plates")
        self.pluginVariable(variableList, 2, 7, "RapidPick")
        self.pluginVariable(variableList, 3, 8, "Solo")
        self.pluginVariable(variableList, 4, 9, "TorreyPinesRIC20")

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
        debugSymbol = ET.SubElement(protocol, "sads:DebugSymbol.Symbol")
        debugSymbol.text = "dxYuXERldlxOZXdQcm90b2NvbC5zbHZwAQEBPAwBAQ=="
        tree = ET.ElementTree(self.indent(protocol))
        tree.write(filename, xml_declaration=True, encoding="utf-8")

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

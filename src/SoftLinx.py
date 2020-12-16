import json
import Properties
import xml.etree.ElementTree as ET


class SoftLinx:
    def __init__(
        self,
        displayName=None,
        filename=None,
        protocolSteps=None,
        plugins=None,
        variables=None,
    ):
        self.displayName = None
        self.filename = None
        self.protocolSteps = []
        self.plugins = []
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
        # *Initialize Plugins
        try:
            if plugins != None:
                self.setPlugins(plugins)
            else:
                self.setPlugins([])
        except Exception as error:
            print("Error setting plugins.")
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

    def setPlugins(self, plugins):
        if not isinstance(plugins, list):
            raise TypeError("Plugins must be a List.")
        self.plugins = plugins

    def setVariables(self, variables):
        if not isinstance(variables, list):
            raise TypeError("Variables must be a List.")
        self.plugins = variables

    def saveProtocol(self, filename=None):
        if filename == None:
            if self.filename != None:
                filename = self.filename
            else:
                raise BaseException("Need to specify a filename to save a protocol.")
        protocol = ET.Element(
            "Protocol",
            {
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
                "xmlns:sads": "http://schemas.microsoft.com/netfx/2010/xaml/activities/debugger",
                "xmlns:sap": "http://schemas.microsoft.com/netfx/2009/xaml/activities/presentation",
                "xmlns:sap2010": "http://schemas.microsoft.com/netfx/2010/xaml/activities/presentation",
                "xmlns:scg": "clr-namespace:System.Collections.Generic;assembly=mscorlib",
                "xmlns:x": "http://schemas.microsoft.com/winfx/2006/xaml",
            },
        )
        activities = ET.SubElement(protocol, "Protocol.Activities")
        # !Capacity changes based on some factor...unclear exactly what though.
        scg_list = ET.SubElement(
            activities, "scg:List", {"x:TypeAgruments": "p:Activity", "Capacity": "0"},
        )
        # TODO: Protocol Steps
        # ...
        activities2 = ET.SubElement(protocol, "Protocol.Activities2")
        scg_list = ET.SubElement(
            activities2, "scg:List", {"x:TypeAgruments": "p:Activity", "Capacity": "0"},
        )
        initialValues = ET.SubElement(protocol, "Protocol.InitialValues")
        scg_dict = ET.SubElement(
            initialValues,
            "scg:Dictionary",
            {"x:TypeArguments": "x:String, hwab:Variable"},
        )
        interfaces = ET.SubElement(protocol, "Protocol.Interfaces")
        # TODO: Plugins
        # ...
        timeConstraints = ET.SubElement(protocol, "Protocol.TimeConstraints")
        scg_list = ET.SubElement(
            timeConstraints,
            "scg:List",
            {"x:TypeArguments": "hwab:TimeConstraint", "Capacity": "0"},
        )
        variables = ET.SubElement(protocol, "Protocol.Variables")
        # TODO: Variables
        # ...
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

import json
import Properties
import ctypes


class SoftLinx:
    def __init__(self, install_path):
        pass

    def load_dlls(self):
        # protocol_design_dll = ctypes.WinDLL(self.install_path + "\\Hudson.SoftLinx.ProtocolDesign.dll")
        # protocol_controls_dll = ctypes.WinDLL(self.install_path + "\\SoftLinxVProtocolControls.dll")
        # workflow_designers_dll = ctypes.WinDLL(self.install_path + "\\SoftLinx.Workflow.Designers.dll")
        # runtime_presentation_dll = ctypes.WinDLL(self.install_path + "\\Hudson.Runtime.Presentation.dll")
        # workflow_activities_dll = ctypes.WinDLL(self.install_path + "\\Hudson.Workflow.Activities.dll")
        runtime_dll = ctypes.WinDLL(self.install_path + "\\Hudson.Runtime.dll")
        # slinx_addin_dll = ctypes.WinDLL(self.install_path + "\\Hudson.SLinx.Addin.dll")
        # plugins_dll = ctypes.WinDLL(self.install_path + "\\Hudson.Plugins.dll")
        # pipeline_host_dll = ctypes.WinDLL(self.install_path + "\\Hudson.Plugins.Pipeline.Host.dll")
        # base_activities_dll = ctypes.WinDLL(self.install_path + "\\SoftLinxBaseActivities.dll")
        # slinx_common_dll = ctypes.WinDLL(self.install_path + "\\Hudson.SLinx.Common.dll")
        # evaluator_dll = ctypes.WinDLL(self.install_path + "\\SoftLinxEvaluator.dll")
        # go_dll = ctypes.WinDLL(self.install_path + "\\Hudson.GO.dll")
        # design_dll = ctypes.WinDLL(self.install_path + "\\Hudson.Design.dll")
        # common_dll = ctypes.WinDLL(self.install_path + "\\Hudson.Common.dll")
        # interop_msapc_dll = ctypes.WinDLL(self.install_path + "\\Interop.MSAPC.dll")
        # ionic_zip_dll = ctypes.WinDLL(self.install_path + "\\Ionic.Zip.dll")
        # easy_hook_dll = ctypes.WinDLL(self.install_path + "\\EasyHook.dll")
        # easy_hook_32_dll = ctypes.WinDLL(self.install_path + "\\EasyHook32.dll")

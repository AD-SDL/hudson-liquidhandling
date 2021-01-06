#SingleInstance, Force
SendMode Input
SetWorkingDir, %A_ScriptDir%

Run, "C:\Program Files (x86)\Hudson Robotics\SoftLinx V\SoftLinxVProtocolEditor.exe" ..\..\..\NewProtocol.slvp
WinActivate, SoftLinx V
WinWaitActive, SoftLinx V
Sleep, 5000
#IfWinActive, SoftLinx V
MouseClick, Left, 300, 45
Sleep, 1000
Send, {Enter}
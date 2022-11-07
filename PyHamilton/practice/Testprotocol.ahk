
#SingleInstance, Force
#WinActivateForce
SendMode Input
SetWorkingDir, %A_ScriptDir%
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
Run, "C:\Program Files (x86)\Hudson Robotics\SoftLinx V\SoftLinxVProtocolEditor.exe" %A_ScriptDir%\Testprotocol.slvp
WinWaitActive, SoftLinx V,,10
if ErrorLevel
{
    WinGetActiveTitle, Title
    MsgBox, Couldn't find SoftLinx V window. The active window is "%Title%".
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
                
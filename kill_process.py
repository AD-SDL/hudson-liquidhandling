# finds and kills softlinx and solosoft in the task manager

import psutil

proc1 = "softlinx.exe" # TODO: change
proc2 = "solo.exe"

for proc in psutil.process_iter():
    if proc.name() == proc1:
        proc.kill()
        print("Softlinx shut down")
    if proc.name() == proc2:
        proc.kill()
        print("Solo shut down")

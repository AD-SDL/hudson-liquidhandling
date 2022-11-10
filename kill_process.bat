:: kills the  softlinx and solosoft processes in windows

:: log date and time

echo %DATE% %TIME% >> C:\labautomation\log\kill_process.log

:: execute python script that kills processes

powershell.exe -Command "& 'C:\ProgramData\Miniconda3\shell\condabin\conda-hook.ps1' ; conda activate 'C:\ProgramData\Miniconda3' ; conda activate jupyter ; python 'C:\Users\svcaibio\Dev\liquidhandling\kill_process.py' >> C:\labautomation\log\kill_softlinx_process.log 2>&1
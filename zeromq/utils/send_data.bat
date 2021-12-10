:: Log date and time
echo %DATE% %TIME% >> C:\labautomation\log\send_data.log

:: Check for plate id argument
IF "%1"=="" (
    SET plate_id = -1
) ELSE (
    SET plate_id = %1
)

powershell.exe -Command "& 'C:\ProgramData\Miniconda3\shell\condabin\conda-hook.ps1' ; conda activate 'C:\ProgramData\Miniconda3' ; conda activate jupyter ; python 'C:\Users\svcaibio\Dev\liquidhandling\zeromq\hudson01_send_data.py' -d 'C:\labautomation\data' -e '.xlsx' -id %plate_id% >> C:\labautomation\log\hudson01_send_data.log 2>&1
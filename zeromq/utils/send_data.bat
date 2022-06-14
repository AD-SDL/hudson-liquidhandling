:: Log date and time
echo %DATE% %TIME% >> C:\labautomation\log\send_data.log

:: Check for plate id argument
IF "%1"=="" (
    SET /A plate_id = -1
) ELSE (
    SET /A plate_id = %1
)

:: Check for experiment name argument 
IF "%2"=="" (
    SET experiment_name=
) ELSE (
    SET experiment_name=%2
)

:: Check for data format argument
IF "%3"=="" (
    SET data_format=
) ELSE (
    SET data_format=%3
)

:: Log command line arguments 
ECHO %plate_id% >> C:\labautomation\log\send_data.log
ECHO %experiment_name% >> C:\labautomation\log\send_data.log
ECHO %data_format% >> C:\labautomation\log\send_data.log

:: send data with call to hudson01_send_data.py
::powershell.exe -Command "& 'C:\ProgramData\Miniconda3\shell\condabin\conda-hook.ps1' ; conda activate 'C:\ProgramData\Miniconda3' ; conda activate jupyter ; python 'C:\Users\svcaibio\Dev\liquidhandling\zeromq\hudson01_send_data.py' -d 'C:\labautomation\data' -e '.xlsx' -id %plate_id% -en %experiment_name% -df %data_format% >> C:\labautomation\log\hudson01_send_data.log 2>&1

powershell.exe -Command "& 'C:\ProgramData\Miniconda3\shell\condabin\conda-hook.ps1' ; conda activate 'C:\ProgramData\Miniconda3' ; conda activate jupyter ; python 'C:\Users\svcaibio\Dev\liquidhandling\zeromq\hudson01_distribute_send_data.py' -d 'C:\labautomation\data' -e '.xlsx' -id %plate_id% -en %experiment_name% -df %data_format% >> C:\labautomation\log\hudson01_distribute_send_data.log 2>&1
:: Log date and time
echo %DATE% %TIME% >> C:\Users\svcaibio\Dev\liquidhandling\peeler_logging\peel.log

:: Check for peel location argument
IF "%1"=="" (
    SET Set_Number=
) ELSE (
    SET Set_Number=%1
)

:: Check for adhere time argument
IF "%2"=="" (
    SET Time=
) ELSE (
    SET Time=%2
)

:: Log command line arguments 
ECHO %Set_Number% >> C:\Users\svcaibio\Dev\liquidhandling\peeler_logging\peel.log
ECHO %Time% >> C:\Users\svcaibio\Dev\liquidhandling\peeler_logging\peel.log

:: Execute peel command with Hudson_Peeler.p
powershell.exe -Command "& 'C:\ProgramData\Miniconda3\shell\condabin\conda-hook.ps1' ; conda activate 'C:\ProgramData\Miniconda3' ; conda activate azenta ; python C:\Users\svcaibio\Dev\azenta_module\azenta_driver\Hudson_Peeler.py -n %Set_Number% -t %Time% >> C:\Users\svcaibio\Dev\liquidhandling\peeler_logging\Hudson_peeler.log 2>&1

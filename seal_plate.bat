:: Log date and time
echo %DATE% %TIME% >> C:\Users\svcaibio\Dev\liquidhandling\sealer_logging\seal.log

:: Check for seal temp argument
IF "%1"=="" (
    SET Temp=
) ELSE (
    SET Temp=%1
)

:: Check for adhere time argument
IF "%2"=="" (
    SET Time=
) ELSE (
    SET Time=%2
)

:: Log command line arguments 
ECHO %Temp% >> C:\Users\svcaibio\Dev\liquidhandling\sealer_logging\seal.log
ECHO %Time% >> C:\Users\svcaibio\Dev\liquidhandling\sealer_logging\seal.log

:: Execute peel command with Hudson_Peeler.p
powershell.exe -Command "& 'C:\ProgramData\Miniconda3\shell\condabin\conda-hook.ps1' ; conda activate 'C:\ProgramData\Miniconda3' ; conda activate azenta ; python C:\Users\svcaibio\Dev\azenta_module\azenta_driver\Hudson_Sealer.py -deg %Temp% -t %Time% >> C:\Users\svcaibio\Dev\liquidhandling\sealer_logging\Hudson_sealer.log 2>&1

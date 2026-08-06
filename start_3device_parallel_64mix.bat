@echo off
setlocal

set "CONFIG=%~1"
if "%CONFIG%"=="" (
    for /f "usebackq delims=" %%F in (`powershell.exe -NoLogo -NoProfile -STA -ExecutionPolicy Bypass -File "%~dp0scripts\select_experiment_yaml.ps1" "%~dp0experiments"`) do set "CONFIG=%%F"
)

if "%CONFIG%"=="" (
    echo No YAML file selected. Bonsai was not opened.
    pause
    exit /b 1
)

echo Selected YAML:
echo %CONFIG%
echo.
echo Workflow:
echo 3device_parallel_64mix.bonsai
echo.

call "%~dp0scripts\run_experiment.cmd" "%CONFIG%" -Workflow "3device_parallel_64mix.bonsai" -OpenOnly
set "EXIT_CODE=%ERRORLEVEL%"

if not "%EXIT_CODE%"=="0" (
    echo.
    echo Bonsai did not open successfully. Error code: %EXIT_CODE%
    echo Check the message above, then press any key to close this window.
    pause
)

endlocal & exit /b %EXIT_CODE%
